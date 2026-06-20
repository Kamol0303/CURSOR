from __future__ import annotations

import secrets

import pyotp

from app.core.security import decrypt_value, encrypt_value, hash_secret


ISSUER = "TaMoR"


def create_totp_secret() -> str:
    return pyotp.random_base32()


def encrypt_totp_secret(secret: str) -> str:
    return encrypt_value(secret)


def provisioning_uri(secret: str, username: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name=ISSUER)


def verify_totp_code(encrypted_secret: str, code: str) -> bool:
    secret = decrypt_value(encrypted_secret)
    return pyotp.TOTP(secret).verify(code, valid_window=1)


def generate_recovery_codes() -> tuple[list[str], list[str]]:
    raw_codes = [secrets.token_hex(4).upper() for _ in range(10)]
    hashed_codes = [hash_secret(code) for code in raw_codes]
    return raw_codes, hashed_codes
