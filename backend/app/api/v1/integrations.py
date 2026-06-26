"""Integration webhooks — Telegram, SMS, Click, Payme."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.logging_config import get_logger
from app.integrations.payment_gateways import (
    is_payme_completion,
    parse_click_payment,
    parse_payme_payment,
    verify_click_signature,
    verify_payme_signature,
)
from app.integrations.sms_adapter import verify_webhook_signature
from app.integrations.telegram_adapter import handle_update, verify_telegram_webhook
from app.models.analytics_notifications import SmsLog
from app.models.finance import PaymentTransaction
from app.models.identity import SecurityEvent
from app.models.operations import StudentPayment
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/integrations", tags=["integrations"])
logger = get_logger(__name__)


class SmsWebhookPayload(BaseModel):
    message_id: str
    status: str
    phone: str | None = None


class TelegramUpdate(BaseModel):
    update_id: int
    message: dict | None = None
    edited_message: dict | None = None


async def _parse_webhook_payload(request: Request) -> dict:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
        return data if isinstance(data, dict) else {}
    body = await request.body()
    if not body:
        return {}
    from urllib.parse import parse_qs

    parsed = parse_qs(body.decode("utf-8", errors="replace"))
    return {k: (v[0] if len(v) == 1 else v) for k, v in parsed.items()}


async def _audit_payment_failure(
    db: AsyncSession,
    *,
    provider: str,
    reason: str,
    ip: str | None,
    details: dict | None = None,
) -> None:
    db.add(
        SecurityEvent(
            event_type=f"payment_webhook_{provider}_rejected",
            severity="high",
            ip_address=ip,
            details={"reason": reason, **(details or {})},
        )
    )
    logger.warning(
        "payment_webhook_rejected provider=%s reason=%s ip=%s",
        provider,
        reason,
        ip,
    )


@router.post("/telegram/webhook", response_model=ApiResponse)
async def telegram_webhook(
    request: Request,
    update: TelegramUpdate,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not verify_telegram_webhook(settings.TELEGRAM_WEBHOOK_SECRET, x_telegram_bot_api_secret_token):
        raise HTTPException(status_code=401, detail={"code": "INVALID_SIGNATURE"})

    response = await handle_update(db, update.model_dump())
    await db.commit()
    if response:
        if settings.TELEGRAM_BOT_TOKEN:
            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={"chat_id": response.chat_id, "text": response.text},
                )
        else:
            print(f"[TELEGRAM STUB] chat={response.chat_id}: {response.text[:100]}")
    return ApiResponse(success=True, data={"received": True})


@router.post("/sms/webhook", response_model=ApiResponse)
async def sms_delivery_webhook(
    request: Request,
    payload: SmsWebhookPayload,
    x_signature: str | None = Header(default=None, alias="X-Signature"),
    db: AsyncSession = Depends(get_db),
):
    body = await request.body()
    if not verify_webhook_signature(body, x_signature):
        raise HTTPException(status_code=401, detail={"code": "INVALID_SIGNATURE"})

    log = SmsLog(
        notification_id=None,
        phone_masked=payload.phone or "***",
        provider="eskiz",
        provider_message_id=payload.message_id,
        status=payload.status,
        raw_response={"webhook": payload.model_dump()},
    )
    db.add(log)
    await db.commit()
    return ApiResponse(success=True, data={"received": True})


@router.post("/click/webhook")
async def click_webhook(
    request: Request,
    x_signature: str | None = Header(default=None, alias="X-Signature"),
    db: AsyncSession = Depends(get_db),
):
    payload = await _parse_webhook_payload(request)
    client_ip = request.client.host if request.client else None

    if not verify_click_signature(payload, x_signature):
        await _audit_payment_failure(
            db,
            provider="click",
            reason="invalid_signature",
            ip=client_ip,
            details={"merchant_trans_id": payload.get("merchant_trans_id")},
        )
        await db.commit()
        raise HTTPException(status_code=403, detail={"code": "INVALID_SIGNATURE"})

    payment_id, amount, external_id, action = parse_click_payment(payload)
    if action != 1:
        return {
            "error": 0,
            "error_note": "Prepare accepted",
            "click_trans_id": payload.get("click_trans_id"),
            "merchant_trans_id": payment_id,
            "merchant_prepare_id": payment_id,
        }

    await _apply_gateway_payment(
        db,
        payment_id=payment_id,
        amount=amount,
        provider="click",
        external_id=external_id,
        payload=payload,
    )
    await db.commit()
    return ApiResponse(success=True, data={"received": True})


@router.post("/payme/webhook")
async def payme_webhook(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_signature: str | None = Header(default=None, alias="X-Signature"),
    db: AsyncSession = Depends(get_db),
):
    payload = await _parse_webhook_payload(request)
    client_ip = request.client.host if request.client else None

    if not verify_payme_signature(payload, authorization=authorization, signature=x_signature):
        await _audit_payment_failure(
            db,
            provider="payme",
            reason="invalid_signature",
            ip=client_ip,
            details={"method": payload.get("method")},
        )
        await db.commit()
        raise HTTPException(status_code=403, detail={"code": "INVALID_SIGNATURE"})

    payment_id, amount, external_id, method = parse_payme_payment(payload)
    if not is_payme_completion(method):
        return ApiResponse(success=True, data={"acknowledged": True, "method": method})

    await _apply_gateway_payment(
        db,
        payment_id=payment_id,
        amount=amount,
        provider="payme",
        external_id=external_id,
        payload=payload,
    )
    await db.commit()
    return ApiResponse(success=True, data={"received": True})


async def _apply_gateway_payment(
    db: AsyncSession,
    *,
    payment_id: str,
    amount: float,
    provider: str,
    external_id: str,
    payload: dict,
) -> None:
    if not payment_id:
        raise HTTPException(status_code=422, detail={"code": "INVALID_PAYLOAD"})
    if not external_id:
        raise HTTPException(status_code=422, detail={"code": "INVALID_PAYLOAD"})

    existing_tx = await db.execute(
        select(PaymentTransaction).where(
            PaymentTransaction.provider == provider,
            PaymentTransaction.external_id == external_id,
        )
    )
    if existing_tx.scalar_one_or_none():
        logger.info("payment_webhook_idempotent provider=%s external_id=%s", provider, external_id)
        return

    try:
        pid = UUID(payment_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "INVALID_PAYLOAD"}) from exc

    result = await db.execute(select(StudentPayment).where(StudentPayment.id == pid))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail={"code": "PAYMENT_NOT_FOUND"})

    if payment.status == "paid" and payment.external_transaction_id == external_id:
        logger.info("payment_already_paid payment_id=%s provider=%s", payment_id, provider)
        return

    expected = float(payment.amount)
    if abs(expected - amount) > 0.01:
        raise HTTPException(
            status_code=422,
            detail={"code": "AMOUNT_MISMATCH", "expected": expected, "received": amount},
        )

    payment.status = "paid"
    payment.paid_at = datetime.now(UTC)
    payment.payment_method = provider
    payment.external_transaction_id = external_id
    db.add(
        PaymentTransaction(
            payment_id=payment.id,
            center_id=payment.center_id,
            amount=amount,
            provider=provider,
            external_id=external_id,
            status="completed",
            raw_payload=payload,
        )
    )
