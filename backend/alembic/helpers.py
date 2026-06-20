"""Alembic migration helpers for PostgreSQL and SQLite."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


def is_postgresql() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def uuid_column(**kwargs) -> sa.Column:
    """Cross-dialect UUID column (native UUID on PostgreSQL, CHAR(32) on SQLite)."""
    if is_postgresql():
        return sa.Column(postgresql.UUID(as_uuid=True), **kwargs)
    return sa.Column(sa.Uuid(), **kwargs)


def enum_column(name: str, values: tuple[str, ...], **kwargs) -> sa.Column:
    """Enum column — native ENUM on PostgreSQL, constrained String on SQLite."""
    if is_postgresql():
        return sa.Column(sa.Enum(*values, name=name), **kwargs)
    return sa.Column(sa.Enum(*values, native_enum=False), **kwargs)
