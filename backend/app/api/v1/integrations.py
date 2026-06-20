from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.integrations.sms_adapter import verify_webhook_signature
from app.models.analytics_notifications import SmsLog
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/integrations", tags=["integrations"])


class SmsWebhookPayload(BaseModel):
    message_id: str
    status: str
    phone: str | None = None


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
