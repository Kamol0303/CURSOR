"""Timezone-safe datetime helpers for DB values and comparisons."""

from datetime import UTC, datetime


def ensure_utc_aware(value: datetime | None) -> datetime | None:
    """Normalize a datetime to UTC-aware form for safe comparisons."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def utc_now() -> datetime:
    return datetime.now(UTC)
