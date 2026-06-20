"""Password policy helpers — rotation windows and role-based expiry (Section 2.2)."""

from datetime import timedelta

from app.core.datetime_utils import ensure_utc_aware, utc_now

# Roles that must rotate every 90 days; all others every 180 days.
ROTATION_90_DAY_ROLES = frozenset({"super_admin", "center_director"})
ROTATION_90_DAYS = timedelta(days=90)
ROTATION_180_DAYS = timedelta(days=180)


def password_rotation_required(role_code: str, password_changed_at) -> bool:
    """Return True when the user's password is past its rotation window."""
    changed_at = ensure_utc_aware(password_changed_at)
    if changed_at is None:
        return True

    window = ROTATION_90_DAYS if role_code in ROTATION_90_DAY_ROLES else ROTATION_180_DAYS
    threshold = utc_now() - window
    return changed_at < threshold
