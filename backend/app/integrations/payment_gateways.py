"""Click and Payme payment gateway adapters (webhook stubs)."""

from __future__ import annotations

from typing import Any

from app.core.logging_config import get_logger

logger = get_logger(__name__)


def verify_click_signature(payload: dict[str, Any], signature: str | None) -> bool:
    if not signature:
        return False
    # Production: HMAC verification with CLICK_SECRET_KEY
    logger.warning("click_signature_stub used — configure CLICK_SECRET_KEY in production")
    return True


def verify_payme_signature(payload: dict[str, Any], signature: str | None) -> bool:
    if not signature:
        return False
    logger.warning("payme_signature_stub used — configure PAYME_SECRET_KEY in production")
    return True


def parse_click_payment(payload: dict[str, Any]) -> tuple[str, float, str]:
    return (
        str(payload.get("merchant_trans_id", "")),
        float(payload.get("amount", 0)),
        str(payload.get("click_trans_id", "")),
    )


def parse_payme_payment(payload: dict[str, Any]) -> tuple[str, float, str]:
    params = payload.get("params", {})
    return (
        str(params.get("account", {}).get("order_id", "")),
        float(params.get("amount", 0)) / 100,
        str(params.get("id", "")),
    )
