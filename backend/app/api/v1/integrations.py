from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.integrations.sms_adapter import verify_webhook_signature
from app.integrations.telegram_adapter import handle_update, verify_telegram_webhook
from app.models.analytics_notifications import SmsLog
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
