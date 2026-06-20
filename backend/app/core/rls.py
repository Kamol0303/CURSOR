"""Set PostgreSQL session variables for Row-Level Security policies."""

from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from app.models.identity import User

_rls_user: ContextVar[User | None] = ContextVar("rls_user", default=None)
_rls_override: ContextVar[str | None] = ContextVar("rls_override", default=None)


def set_rls_user(user: User | None) -> None:
    _rls_user.set(user)


def set_rls_role(role: str) -> None:
    _rls_override.set(role)


def clear_rls_context() -> None:
    _rls_user.set(None)
    _rls_override.set(None)


async def apply_rls_context(session: AsyncSession) -> None:
    override = _rls_override.get()
    user = _rls_user.get()

    if override:
        role = override
        center_id = ""
        phone = ""
    elif user:
        role = user.role.code
        center_id = str(user.center_id) if user.center_id else ""
        phone = user.phone or ""
    else:
        role = "anonymous"
        center_id = ""
        phone = ""

    await session.execute(text("SELECT set_config('app.role', :role, true)"), {"role": role})
    await session.execute(text("SELECT set_config('app.center_id', :cid, true)"), {"cid": center_id})
    await session.execute(text("SELECT set_config('app.phone', :phone, true)"), {"phone": phone})
