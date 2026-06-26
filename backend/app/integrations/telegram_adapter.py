"""Telegram bot adapter — webhook handler with signature validation."""

from __future__ import annotations

import hmac
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.integrations import TelegramSubscription


@dataclass
class TelegramResponse:
    chat_id: int
    text: str


def verify_telegram_webhook(secret_token: str | None, header_token: str | None) -> bool:
    if settings.ENVIRONMENT in {"development", "test"} and not header_token:
        return True
    if not settings.TELEGRAM_WEBHOOK_SECRET:
        return False
    if not header_token:
        return False
    return hmac.compare_digest(settings.TELEGRAM_WEBHOOK_SECRET, header_token)


async def ensure_subscription(db: AsyncSession, chat_id: int, locale: str = "uz") -> TelegramSubscription:
    result = await db.execute(select(TelegramSubscription).where(TelegramSubscription.chat_id == chat_id))
    sub = result.scalar_one_or_none()
    if sub:
        return sub
    sub = TelegramSubscription(chat_id=chat_id, locale=locale)
    db.add(sub)
    await db.flush()
    return sub


async def handle_update(db: AsyncSession, update: dict) -> TelegramResponse | None:
    message = update.get("message") or update.get("edited_message")
    if not message:
        return None

    chat_id = message["chat"]["id"]
    text = (message.get("text") or "").strip()
    await ensure_subscription(db, chat_id)

    if text.startswith("/start"):
        return TelegramResponse(
            chat_id=chat_id,
            text=(
                "TMB botiga xush kelibsiz!\n"
                "Buyruqlar:\n"
                "/verify TMB-XXXX — sertifikatni tekshirish\n"
                "/status — bot holati"
            ),
        )

    if text.startswith("/verify"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            return TelegramResponse(chat_id=chat_id, text="Sertifikat raqamini kiriting: /verify TMB-2026-XXX")
        cert_number = parts[1].strip()
        from app.core.rls import apply_rls_context, set_rls_role
        from app.services import certificate_service

        set_rls_role("verifier")
        await apply_rls_context(db)
        result = await certificate_service.verify_certificate_public(db, cert_number, locale="uz")
        if result.get("valid"):
            return TelegramResponse(
                chat_id=chat_id,
                text=f"✅ Sertifikat haqiqiy\n{result.get('holder_name', '')}\n{result.get('course_name', '')}",
            )
        return TelegramResponse(chat_id=chat_id, text="❌ Sertifikat topilmadi yoki haqiqiy emas")

    if text.startswith("/status"):
        return TelegramResponse(chat_id=chat_id, text="TMB bot faol. Toyloq tumani ta'lim monitoringi.")

    return TelegramResponse(chat_id=chat_id, text="Noma'lum buyruq. /start yordam uchun.")
