import hashlib
import hmac

from app.integrations.sms_adapter import mask_phone, verify_webhook_signature


def test_mask_phone():
    assert mask_phone("+998901234567") == "+998***67"


def test_webhook_signature_valid():
    payload = b'{"message_id":"abc","status":"delivered"}'
    secret = "test-secret"
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_webhook_signature(payload, sig, secret=secret)


def test_webhook_signature_invalid():
    assert not verify_webhook_signature(b"{}", "bad-signature", secret="test-secret")
