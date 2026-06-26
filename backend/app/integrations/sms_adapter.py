"""SMS adapter — eskiz.uz with webhook signature validation."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.integrations.http_client import SSRFError, validate_external_url

ESKIZ_SEND_URL = "https://notify.eskiz.uz/api/message/sms/send"
ESKIZ_LOGIN_URL = "https://notify.eskiz.uz/api/auth/login"


@dataclass
class SmsResult:
    success: bool
    provider_message_id: str | None
    error: str | None = None
    raw_response: dict | None = None


def mask_phone(phone: str) -> str:
    digits = phone.replace("+", "").replace(" ", "")
    if len(digits) < 6:
        return "***"
    return f"+{digits[:3]}***{digits[-2:]}"


def verify_webhook_signature(payload: bytes, signature: str | None, secret: str | None = None) -> bool:
    if not signature:
        return False
    key = (secret or settings.SMS_WEBHOOK_SECRET).encode()
    expected = hmac.new(key, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


async def _get_eskiz_token() -> str | None:
    if settings.ESKIZ_API_TOKEN:
        return settings.ESKIZ_API_TOKEN
    if not settings.ESKIZ_EMAIL or not settings.ESKIZ_PASSWORD:
        return None
    try:
        validate_external_url(ESKIZ_LOGIN_URL)
    except SSRFError:
        return None
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            ESKIZ_LOGIN_URL,
            data={"email": settings.ESKIZ_EMAIL, "password": settings.ESKIZ_PASSWORD},
        )
        if response.status_code != 200:
            return None
        return response.json().get("data", {}).get("token")


async def send_sms(phone: str, message: str) -> SmsResult:
    if settings.ENVIRONMENT in {"development", "test"}:
        print(f"[SMS STUB] To {mask_phone(phone)}: {message[:80]}...")
        return SmsResult(
            success=True,
            provider_message_id=f"stub_{secrets.token_hex(8)}",
            raw_response={"status": "queued", "provider": "eskiz_stub"},
        )

    token = await _get_eskiz_token()
    if not token:
        return SmsResult(success=False, provider_message_id=None, error="SMS gateway not configured")

    try:
        validate_external_url(ESKIZ_SEND_URL)
    except SSRFError as exc:
        return SmsResult(success=False, provider_message_id=None, error=str(exc))

    # Normalize phone for eskiz (998XXXXXXXXX)
    normalized = phone.replace("+", "").replace(" ", "")

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            ESKIZ_SEND_URL,
            headers={"Authorization": f"Bearer {token}"},
            data={
                "mobile_phone": normalized,
                "message": message,
                "from": "4546",
            },
        )
        body = response.json() if response.content else {}
        if response.status_code == 200 and body.get("status") == "waiting":
            msg_id = str(body.get("id", secrets.token_hex(8)))
            return SmsResult(success=True, provider_message_id=msg_id, raw_response=body)
        return SmsResult(
            success=False,
            provider_message_id=None,
            error=body.get("message", f"HTTP {response.status_code}"),
            raw_response=body,
        )
