from uuid import UUID

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.integrations.payment_gateways import (
    parse_click_payment,
    parse_payme_payment,
    verify_click_signature,
    verify_payme_signature,
)
from app.integrations.sms_adapter import verify_webhook_signature
from app.integrations.telegram_adapter import handle_update, verify_telegram_webhook
from app.models.analytics_notifications import SmsLog
from app.models.finance import PaymentTransaction
from app.models.operations import StudentPayment
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/integrations", tags=["integrations"])


class SmsWebhookPayload(BaseModel):
    message_id: str
    status: str
    phone: str | None = None


class TelegramUpdate(BaseModel):
    update_id: int
    message: dict | None = None
    edited_message: dict | None = None


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


@router.post("/click/webhook", response_model=ApiResponse)
async def click_webhook(
    request: Request,
    x_signature: str | None = Header(default=None, alias="X-Signature"),
    db: AsyncSession = Depends(get_db),
):
    payload = await request.json()
    if not verify_click_signature(payload, x_signature):
        raise HTTPException(status_code=401, detail={"code": "INVALID_SIGNATURE"})
    payment_id, amount, external_id = parse_click_payment(payload)
    await _apply_gateway_payment(db, payment_id=payment_id, amount=amount, provider="click", external_id=external_id, payload=payload)
    await db.commit()
    return ApiResponse(success=True, data={"received": True})


@router.post("/payme/webhook", response_model=ApiResponse)
async def payme_webhook(
    request: Request,
    x_signature: str | None = Header(default=None, alias="X-Signature"),
    db: AsyncSession = Depends(get_db),
):
    payload = await request.json()
    if not verify_payme_signature(payload, x_signature):
        raise HTTPException(status_code=401, detail={"code": "INVALID_SIGNATURE"})
    payment_id, amount, external_id = parse_payme_payment(payload)
    await _apply_gateway_payment(db, payment_id=payment_id, amount=amount, provider="payme", external_id=external_id, payload=payload)
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
    try:
        pid = UUID(payment_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "INVALID_PAYLOAD"}) from exc
    result = await db.execute(select(StudentPayment).where(StudentPayment.id == pid))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail={"code": "PAYMENT_NOT_FOUND"})
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
