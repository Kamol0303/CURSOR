import pytest
from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    is_valid_bcrypt_hash,
    validate_password_policy,
    verify_password,
    verify_totp,
    generate_totp_secret,
)


class TestPasswordPolicy:
    def test_valid_password(self):
        valid, code = validate_password_policy("Tamor#2026Admin!")
        assert valid is True
        assert code is None

    def test_too_short(self):
        valid, code = validate_password_policy("Short1!")
        assert valid is False
        assert code == "PASSWORD_TOO_SHORT"

    def test_missing_uppercase(self):
        valid, code = validate_password_policy("tamor#2026admin!")
        assert valid is False
        assert code == "PASSWORD_MISSING_UPPERCASE"

    def test_missing_special(self):
        valid, code = validate_password_policy("Tamor2026Admin")
        assert valid is False
        assert code == "PASSWORD_MISSING_SPECIAL"

    def test_breached_password(self):
        import app.core.security as sec
        sec._breached_passwords = None
        valid, code = validate_password_policy("Password123!")
        assert valid is False
        assert code == "PASSWORD_BREACHED"


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "Tamor#2026Admin!"
        hashed = hash_password(password)
        assert verify_password(password, hashed)
        assert not verify_password("wrong", hashed)

    def test_invalid_hash_returns_false(self):
        assert not verify_password("any", "not-a-bcrypt-hash")
        assert not verify_password("any", None)
        assert not is_valid_bcrypt_hash("plaintext-password")


class TestJWT:
    def test_create_and_decode(self):
        token = create_access_token(
            user_id="test-user-id",
            role="super_admin",
            center_id=None,
            permissions=["centers.read"],
            locale="uz",
        )
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "test-user-id"
        assert payload["role"] == "super_admin"
        assert payload["locale"] == "uz"

    def test_invalid_token(self):
        assert decode_access_token("invalid.token.here") is None


class TestRefreshToken:
    def test_token_hashing(self):
        token = generate_refresh_token()
        hashed = hash_token(token)
        assert len(hashed) == 64
        assert hash_token(token) == hashed


class TestTOTP:
    def test_totp_generation_and_verify(self):
        secret = generate_totp_secret()
        import pyotp
        totp = pyotp.TOTP(secret)
        code = totp.now()
        assert verify_totp(secret, code)
