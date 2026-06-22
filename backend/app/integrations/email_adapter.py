"""Email adapter — SMTP (Gmail etc.) for staging/production; stub in dev/test."""

from __future__ import annotations

import asyncio
import smtplib
import uuid
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


@dataclass
class EmailResult:
    success: bool
    message_id: str | None
    error: str | None = None


def _send_smtp_sync(*, to: str, subject: str, body: str) -> EmailResult:
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return EmailResult(success=False, message_id=None, error="SMTP not configured")

    from_header = settings.SMTP_FROM or f"TMB <{settings.SMTP_USER}>"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_header
    msg["To"] = to
    msg.attach(MIMEText(body, "plain", "utf-8"))

    message_id = f"<{uuid.uuid4()}@{settings.SMTP_HOST}>"

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, [to], msg.as_string())

    return EmailResult(success=True, message_id=message_id)


async def send_email(to: str, subject: str, body: str) -> EmailResult:
    if settings.ENVIRONMENT in {"development", "test"}:
        print(f"[EMAIL STUB] To {to}: {subject}")
        return EmailResult(success=True, message_id=f"email_stub_{hash(to + subject) & 0xFFFFFF:06x}")

    try:
        return await asyncio.to_thread(
            _send_smtp_sync,
            to=to,
            subject=subject,
            body=body,
        )
    except Exception as exc:
        return EmailResult(success=False, message_id=None, error=str(exc))
