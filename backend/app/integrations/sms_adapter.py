"""SMS adapter — eskiz.uz stub with webhook signature validation."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass

from app.core.config import settings


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


async def send_sms(phone: str, message: str) -> SmsResult:
    if settings.ENVIRONMENT in {"development", "test"}:
        print(f"[SMS STUB] To {mask_phone(phone)}: {message[:80]}...")
        return SmsResult(
            success=True,
            provider_message_id=f"stub_{secrets.token_hex(8)}",
            raw_response={"status": "queued", "provider": "eskiz_stub"},
        )

    if not settings.ESKIZ_API_TOKEN:
        return SmsResult(success=False, provider_message_id=None, error="SMS gateway not configured")

    # Production would call eskiz.uz API via SSRF-safe client
    return SmsResult(
        success=False,
        provider_message_id=None,
        error="Eskiz integration not enabled in this environment",
    )
