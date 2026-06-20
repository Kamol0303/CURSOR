"""Email adapter stub — logs in dev, no-op in production until configured."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass
class EmailResult:
    success: bool
    message_id: str | None
    error: str | None = None


async def send_email(to: str, subject: str, body: str) -> EmailResult:
    if settings.ENVIRONMENT in {"development", "test"}:
        print(f"[EMAIL STUB] To {to}: {subject}")
        return EmailResult(success=True, message_id=f"email_stub_{hash(to + subject) & 0xFFFFFF:06x}")

    if not settings.SMTP_HOST:
        return EmailResult(success=False, message_id=None, error="SMTP not configured")

    return EmailResult(success=False, message_id=None, error="SMTP integration not enabled")
