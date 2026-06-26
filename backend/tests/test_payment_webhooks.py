"""Payment gateway webhook signature and parsing tests."""

import base64
import hashlib

import pytest

from app.core.config import settings
from app.integrations.payment_gateways import (
    compute_click_sign_string,
    is_payme_completion,
    parse_click_payment,
    parse_payme_payment,
    verify_click_signature,
    verify_payme_signature,
)


@pytest.fixture(autouse=True)
def _payment_env(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "test")
    monkeypatch.setattr(settings, "CLICK_SERVICE_ID", "12345")
    monkeypatch.setattr(settings, "CLICK_SECRET_KEY", "test-click-secret")
    monkeypatch.setattr(settings, "PAYME_SECRET_KEY", "test-payme-secret")
    monkeypatch.setattr(settings, "PAYME_MERCHANT_LOGIN", "Paycom")
    monkeypatch.setattr(settings, "PAYMENT_WEBHOOK_ALLOW_UNSIGNED_DEV", False)


def _click_payload(*, action: int = 1, merchant_prepare_id: str = "prep-1") -> dict:
    payload = {
        "click_trans_id": "3001234567",
        "service_id": settings.CLICK_SERVICE_ID,
        "merchant_trans_id": "550e8400-e29b-41d4-a716-446655440000",
        "amount": "150000",
        "action": action,
        "sign_time": "2026-06-20 12:00:00",
    }
    if action == 1:
        payload["merchant_prepare_id"] = merchant_prepare_id
    payload["sign_string"] = compute_click_sign_string(payload)
    return payload


def test_click_signature_valid_complete():
    payload = _click_payload(action=1)
    assert verify_click_signature(payload) is True


def test_click_signature_valid_prepare():
    payload = _click_payload(action=0)
    assert verify_click_signature(payload) is True


def test_click_signature_rejects_tampered():
    payload = _click_payload()
    payload["amount"] = "999999"
    assert verify_click_signature(payload) is False


def test_click_signature_rejects_missing_sign():
    payload = _click_payload()
    del payload["sign_string"]
    assert verify_click_signature(payload, signature=None) is False


def test_click_rejects_without_config(monkeypatch):
    monkeypatch.setattr(settings, "CLICK_SECRET_KEY", "")
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    payload = _click_payload()
    assert verify_click_signature(payload) is False


def test_payme_basic_auth_valid():
    token = base64.b64encode(b"Paycom:test-payme-secret").decode()
    assert verify_payme_signature({}, authorization=f"Basic {token}") is True


def test_payme_basic_auth_invalid():
    token = base64.b64encode(b"Paycom:wrong-secret").decode()
    assert verify_payme_signature({}, authorization=f"Basic {token}") is False


def test_payme_json_rpc_parse():
    payload = {
        "method": "PerformTransaction",
        "params": {
            "id": "tx-99",
            "amount": 15000000,
            "account": {"order_id": "550e8400-e29b-41d4-a716-446655440000"},
        },
    }
    order_id, amount, external_id, method = parse_payme_payment(payload)
    assert order_id == "550e8400-e29b-41d4-a716-446655440000"
    assert amount == 150000.0
    assert external_id == "tx-99"
    assert method == "PerformTransaction"
    assert is_payme_completion(method) is True


def test_parse_click_payment():
    payload = _click_payload()
    payment_id, amount, external_id, action = parse_click_payment(payload)
    assert payment_id == "550e8400-e29b-41d4-a716-446655440000"
    assert amount == 150000.0
    assert external_id == "3001234567"
    assert action == 1


def test_payme_hmac_legacy_header(monkeypatch):
    import hmac as hmac_mod
    import json

    monkeypatch.setattr(settings, "PAYME_WEBHOOK_HMAC_SECRET", "hmac-secret")
    payload = {"params": {"id": "1"}}
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    sig = hmac_mod.new(settings.PAYME_WEBHOOK_HMAC_SECRET.encode(), body, hashlib.sha256).hexdigest()
    assert verify_payme_signature(payload, signature=sig) is True
