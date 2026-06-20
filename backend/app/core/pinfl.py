import hashlib
import re

from cryptography.fernet import Fernet

from app.core.config import settings


PINFL_PATTERN = re.compile(r"^\d{14}$")


def _pinfl_fernet() -> Fernet:
    import base64

    raw = hashlib.sha256(settings.PINFL_ENCRYPTION_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(raw))


def validate_pinfl(pinfl: str) -> bool:
    return bool(PINFL_PATTERN.match(pinfl))


def encrypt_pinfl(pinfl: str) -> str:
    return _pinfl_fernet().encrypt(pinfl.encode()).decode()


def decrypt_pinfl(encrypted: str) -> str:
    return _pinfl_fernet().decrypt(encrypted.encode()).decode()


def mask_pinfl(pinfl: str) -> str:
    if len(pinfl) < 5:
        return "•••••"
    return "••••••" + pinfl[-5:]
