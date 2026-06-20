from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings
from app.core.security import verify_password


settings = get_settings()


@lru_cache
def load_breached_passwords() -> set[str]:
    path = Path(settings.breached_passwords_path)
    if not path.exists():
        return set()
    return {line.strip().lower() for line in path.read_text().splitlines() if line.strip()}


def validate_password_strength(password: str) -> list[str]:
    errors: list[str] = []
    if len(password) < 12:
        errors.append("PASSWORD_TOO_SHORT")
    if password.lower() == password:
        errors.append("PASSWORD_MISSING_UPPERCASE")
    if password.upper() == password:
        errors.append("PASSWORD_MISSING_LOWERCASE")
    if not any(char.isdigit() for char in password):
        errors.append("PASSWORD_MISSING_DIGIT")
    if not any(not char.isalnum() for char in password):
        errors.append("PASSWORD_MISSING_SPECIAL")
    if password.lower() in load_breached_passwords():
        errors.append("PASSWORD_COMPROMISED")
    return errors


def validate_password_history(password: str, previous_hashes: list[str]) -> list[str]:
    for hashed in previous_hashes[:5]:
        if verify_password(password, hashed):
            return ["PASSWORD_REUSED"]
    return []


def password_rotation_required(role_code: str, password_changed_at: datetime | None) -> bool:
    if password_changed_at is None:
        return True

    days = 90 if role_code in {"super_admin", "center_director"} else 180
    threshold = datetime.now(timezone.utc) - timedelta(days=days)
    return password_changed_at < threshold
