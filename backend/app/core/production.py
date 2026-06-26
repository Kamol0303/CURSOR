"""Production environment validation — fail fast on unsafe configuration."""

from __future__ import annotations

from pathlib import Path

from app.core.config import settings

DEV_SECRET_MARKERS = (
    "dev-only",
    "change-in-prod",
    "change-me",
    "tamor_dev",
)


def _is_dev_secret(value: str) -> bool:
    lower = value.lower()
    return any(marker in lower for marker in DEV_SECRET_MARKERS)


def validate_production_settings() -> list[str]:
    """Return list of blocking errors. Empty list means OK."""
    if settings.ENVIRONMENT != "production":
        return []

    errors: list[str] = []

    if settings.DEBUG:
        errors.append("DEBUG must be False in production")

    for name, value in [
        ("TOTP_ENCRYPTION_KEY", settings.TOTP_ENCRYPTION_KEY),
        ("PINFL_ENCRYPTION_KEY", settings.PINFL_ENCRYPTION_KEY),
        ("SMS_WEBHOOK_SECRET", settings.SMS_WEBHOOK_SECRET),
        ("TELEGRAM_WEBHOOK_SECRET", settings.TELEGRAM_WEBHOOK_SECRET),
        ("CLICK_SECRET_KEY", settings.CLICK_SECRET_KEY),
        ("PAYME_SECRET_KEY", settings.PAYME_SECRET_KEY),
    ]:
        if len(value) < 32:
            errors.append(f"{name} must be at least 32 characters in production")
        if _is_dev_secret(value):
            errors.append(f"{name} appears to be a development default")

    if settings.SECRETS_BACKEND != "vault" and settings.ENVIRONMENT == "production":
        errors.append("SECRETS_BACKEND must be 'vault' in production")

    if not Path(settings.JWT_PRIVATE_KEY_PATH).exists():
        errors.append(f"JWT private key missing at {settings.JWT_PRIVATE_KEY_PATH}")

    if any("localhost" in o for o in settings.CORS_ORIGINS):
        errors.append("CORS_ORIGINS must not include localhost in production")

    if not settings.CLICK_SERVICE_ID:
        errors.append("CLICK_SERVICE_ID is required in production")
    if settings.PAYMENT_WEBHOOK_ALLOW_UNSIGNED_DEV:
        errors.append("PAYMENT_WEBHOOK_ALLOW_UNSIGNED_DEV must be False in production")

    return errors


async def validate_no_demo_accounts(session) -> str | None:
    """Return error message if demo accounts exist (for pre-deploy gate)."""
    from sqlalchemy import func, select

    from app.models.identity import User

    count = (
        await session.execute(select(func.count()).select_from(User).where(User.is_demo_account.is_(True)))
    ).scalar() or 0
    if count > 0:
        return f"Found {count} demo accounts (is_demo_account=true) — run purge_demo_data.py first"
    return None
