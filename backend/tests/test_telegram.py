from app.integrations.telegram_adapter import verify_telegram_webhook


def test_telegram_webhook_dev_mode():
    assert verify_telegram_webhook(None, None) is True


def test_telegram_webhook_rejects_invalid(monkeypatch):
    from app.core import config

    monkeypatch.setattr(config.settings, "TELEGRAM_WEBHOOK_SECRET", "secret")
    monkeypatch.setattr(config.settings, "ENVIRONMENT", "production")
    assert verify_telegram_webhook("secret", "wrong") is False
    assert verify_telegram_webhook("secret", "secret") is True
