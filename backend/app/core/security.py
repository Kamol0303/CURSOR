from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet

from app.core.config import get_settings


settings = get_settings()
password_hasher = PasswordHasher()
fernet = Fernet(settings.mfa_encryption_key.encode())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def ensure_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def generate_opaque_token() -> str:
    return secrets.token_urlsafe(48)


def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()


def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()


def create_access_token(*, subject: str, role: str, permissions: list[str], center_id: str | None, locale: str) -> str:
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "permissions": permissions,
        "center_id": center_id,
        "locale": locale,
        "jti": str(uuid.uuid4()),
        "iat": int(now_utc().timestamp()),
        "exp": int((now_utc() + timedelta(minutes=settings.access_token_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_private_key, algorithm="RS256")


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_public_key, algorithms=["RS256"])


def generate_family_id() -> str:
    return secrets.token_hex(16)


def build_hmac_signature(secret: str, method: str, path: str, timestamp: str, body: bytes) -> str:
    body_hash = hashlib.sha256(body).hexdigest()
    payload = "\n".join([method.upper(), path, timestamp, body_hash])
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()


def verify_hmac_signature(secret: str, method: str, path: str, timestamp: str, body: bytes, signature: str) -> bool:
    expected = build_hmac_signature(secret, method, path, timestamp, body)
    return hmac.compare_digest(expected, signature)


def serialize_device_info(user_agent: str | None, extra: dict[str, Any] | None = None) -> str:
    payload = {"user_agent": user_agent}
    if extra:
        payload.update(extra)
    return json.dumps(payload)
