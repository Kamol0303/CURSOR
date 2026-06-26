"""Click and Payme payment gateway adapters — signature verification and parsing."""

from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Any

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def _secrets_required() -> bool:
    return settings.ENVIRONMENT in ("production", "staging")


def _click_configured() -> bool:
    return bool(settings.CLICK_SECRET_KEY and settings.CLICK_SERVICE_ID)


def _payme_configured() -> bool:
    return bool(settings.PAYME_SECRET_KEY)


def compute_click_sign_string(payload: dict[str, Any]) -> str:
    """Click SHOP-API MD5 signature (official docs).

    Prepare (action=0): click_trans_id + service_id + secret + merchant_trans_id + amount + action + sign_time
    Complete (action=1): adds merchant_prepare_id before amount.
    """
    action = int(payload.get("action", 0))
    parts = [
        str(payload.get("click_trans_id", "")),
        str(settings.CLICK_SERVICE_ID),
        settings.CLICK_SECRET_KEY,
        str(payload.get("merchant_trans_id", "")),
    ]
    if action == 1:
        parts.append(str(payload.get("merchant_prepare_id", "")))
    parts.extend(
        [
            str(payload.get("amount", "")),
            str(action),
            str(payload.get("sign_time", "")),
        ]
    )
    return hashlib.md5("".join(parts).encode()).hexdigest()


def verify_click_signature(payload: dict[str, Any], signature: str | None = None) -> bool:
    """Verify Click webhook using sign_string from body or optional header."""
    provided = str(payload.get("sign_string") or signature or "").strip()
    if not provided:
        return False

    if not _click_configured():
        if _secrets_required():
            logger.error("click_webhook_rejected_missing_config environment=%s", settings.ENVIRONMENT)
            return False
        if settings.PAYMENT_WEBHOOK_ALLOW_UNSIGNED_DEV:
            logger.warning("click_unsigned_allowed_dev — set CLICK_SECRET_KEY for real verification")
            return True
        return False

    expected = compute_click_sign_string(payload)
    return hmac.compare_digest(expected.lower(), provided.lower())


def verify_payme_signature(
    payload: dict[str, Any],
    authorization: str | None = None,
    signature: str | None = None,
) -> bool:
    """Verify Payme Merchant API via Basic Auth (Paycom:SECRET_KEY).

    Legacy X-Signature HMAC header is supported when PAYME_WEBHOOK_HMAC_SECRET is set.
    """
    if authorization and authorization.startswith("Basic "):
        if not _payme_configured():
            if _secrets_required():
                logger.error("payme_webhook_rejected_missing_config environment=%s", settings.ENVIRONMENT)
                return False
            if settings.PAYMENT_WEBHOOK_ALLOW_UNSIGNED_DEV:
                logger.warning("payme_unsigned_allowed_dev — set PAYME_SECRET_KEY for real verification")
                return True
            return False
        try:
            decoded = base64.b64decode(authorization[6:].strip(), validate=True).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return False
        login, _, password = decoded.partition(":")
        expected_login = settings.PAYME_MERCHANT_LOGIN
        return hmac.compare_digest(login, expected_login) and hmac.compare_digest(
            password, settings.PAYME_SECRET_KEY
        )

    if signature and settings.PAYME_WEBHOOK_HMAC_SECRET:
        import json

        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        expected = hmac.new(
            settings.PAYME_WEBHOOK_HMAC_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    if not _secrets_required() and settings.PAYMENT_WEBHOOK_ALLOW_UNSIGNED_DEV and signature:
        logger.warning("payme_legacy_signature_header_dev_only")
        return True

    return False


def parse_click_payment(payload: dict[str, Any]) -> tuple[str, float, str, int]:
    action = int(payload.get("action", 1))
    return (
        str(payload.get("merchant_trans_id", "")),
        float(payload.get("amount", 0)),
        str(payload.get("click_trans_id", "")),
        action,
    )


def parse_payme_payment(payload: dict[str, Any]) -> tuple[str, float, str, str | None]:
    """Parse Payme JSON-RPC or simplified webhook body."""
    method = payload.get("method")
    params = payload.get("params") or {}
    if method:
        account = params.get("account") or {}
        order_id = account.get("order_id") or account.get("payment_id") or ""
        amount_raw = params.get("amount", 0)
        amount = float(amount_raw) / 100 if amount_raw else 0.0
        external_id = str(params.get("id", ""))
        return str(order_id), amount, external_id, method

    nested = params if params else payload
    account = nested.get("account") or {}
    return (
        str(account.get("order_id", "")),
        float(nested.get("amount", 0)) / 100,
        str(nested.get("id", "")),
        None,
    )


def is_payme_completion(method: str | None) -> bool:
    """Only mark paid on PerformTransaction (or simplified webhook without method)."""
    return method is None or method == "PerformTransaction"
