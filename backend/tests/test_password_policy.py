from datetime import datetime, timedelta, timezone

from app.services.password_policy import (
    password_rotation_required,
    validate_password_history,
    validate_password_strength,
)
from app.core.security import hash_password


def test_password_strength_rules():
    assert "PASSWORD_TOO_SHORT" in validate_password_strength("Short1!")
    assert "PASSWORD_MISSING_SPECIAL" in validate_password_strength("Password1234")
    assert validate_password_strength("Strong#Password2026!") == []


def test_password_history_reuse_detection():
    password_hash = hash_password("Reuse#Password2026!")
    assert validate_password_history("Reuse#Password2026!", [password_hash]) == ["PASSWORD_REUSED"]


def test_password_rotation_window_depends_on_role():
    recent = datetime.now(timezone.utc) - timedelta(days=30)
    stale_admin = datetime.now(timezone.utc) - timedelta(days=91)
    stale_teacher = datetime.now(timezone.utc) - timedelta(days=181)

    assert password_rotation_required("super_admin", stale_admin) is True
    assert password_rotation_required("teacher", stale_teacher) is True
    assert password_rotation_required("teacher", recent) is False
