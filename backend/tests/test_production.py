from pathlib import Path

import pytest

from app.core.production import validate_production_settings


@pytest.fixture
def prod_settings(monkeypatch, tmp_path: Path):
    from app.core import config

    priv = tmp_path / "jwt_private.pem"
    pub = tmp_path / "jwt_public.pem"
    priv.write_text("fake-private")
    pub.write_text("fake-public")

    monkeypatch.setattr(config.settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(config.settings, "DEBUG", False)
    monkeypatch.setattr(config.settings, "JWT_PRIVATE_KEY_PATH", str(priv))
    monkeypatch.setattr(config.settings, "JWT_PUBLIC_KEY_PATH", str(pub))
    monkeypatch.setattr(config.settings, "SECRETS_BACKEND", "vault")
    monkeypatch.setattr(config.settings, "TOTP_ENCRYPTION_KEY", "production-grade-key-32-chars-ok!")
    monkeypatch.setattr(config.settings, "PINFL_ENCRYPTION_KEY", "production-grade-key-32-chars-ok!")
    monkeypatch.setattr(config.settings, "SMS_WEBHOOK_SECRET", "production-grade-key-32-chars-ok!!")
    monkeypatch.setattr(config.settings, "TELEGRAM_WEBHOOK_SECRET", "production-grade-key-32-chars-ok!")
    monkeypatch.setattr(config.settings, "CLICK_SERVICE_ID", "12345")
    monkeypatch.setattr(config.settings, "CLICK_SECRET_KEY", "production-grade-click-secret-32chars!")
    monkeypatch.setattr(config.settings, "PAYME_SECRET_KEY", "production-grade-payme-secret-32chars!")
    monkeypatch.setattr(config.settings, "PAYMENT_WEBHOOK_ALLOW_UNSIGNED_DEV", False)
    monkeypatch.setattr(config.settings, "CORS_ORIGINS", ["https://tamor.toyloq.uz"])
    return config.settings


def test_production_valid_baseline(prod_settings):
    errors = validate_production_settings()
    assert errors == []


def test_production_rejects_debug(prod_settings):
    prod_settings.DEBUG = True
    errors = validate_production_settings()
    assert any("DEBUG" in e for e in errors)


def test_production_rejects_dev_secrets(prod_settings):
    prod_settings.TOTP_ENCRYPTION_KEY = "dev-only-change-in-production-32bytes!!"
    errors = validate_production_settings()
    assert any("TOTP" in e for e in errors)


def test_development_skips_validation(monkeypatch):
    from app.core import config

    monkeypatch.setattr(config.settings, "ENVIRONMENT", "development")
    errors = validate_production_settings()
    assert errors == []
