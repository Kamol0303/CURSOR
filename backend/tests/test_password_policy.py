from datetime import UTC, datetime, timedelta

from app.core.datetime_utils import ensure_utc_aware
from app.services.password_policy import password_rotation_required


def test_password_rotation_required_when_never_changed():
    assert password_rotation_required("center_admin", None) is True


def test_password_rotation_naive_datetime_does_not_raise():
    # Simulates PostgreSQL returning a naive timestamp (common driver behavior).
    changed_at = datetime.utcnow() - timedelta(days=200)
    assert password_rotation_required("center_admin", changed_at) is True


def test_password_rotation_aware_datetime():
    changed_at = datetime.now(UTC) - timedelta(days=10)
    assert password_rotation_required("center_admin", changed_at) is False


def test_password_rotation_90_day_role():
    changed_at = datetime.now(UTC) - timedelta(days=100)
    assert password_rotation_required("super_admin", changed_at) is True


def test_ensure_utc_aware_normalizes_naive():
    naive = datetime(2026, 1, 1, 12, 0, 0)
    aware = ensure_utc_aware(naive)
    assert aware is not None
    assert aware.tzinfo is not None
