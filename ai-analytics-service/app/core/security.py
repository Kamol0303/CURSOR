from pathlib import Path

from jose import jwt
from jose.exceptions import JWTError

from app.core.config import settings

_public_key: str | None = None


def _load_public_key() -> str:
    global _public_key
    if _public_key is None:
        path = Path(settings.JWT_PUBLIC_KEY_PATH)
        _public_key = path.read_text()
    return _public_key


def verify_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, _load_public_key(), algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
