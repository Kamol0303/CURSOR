"""Set PostgreSQL session variables for Row-Level Security policies."""

from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

from sqlalchemy import select, text
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
        student_id = ""
        teacher_id = ""
    elif user:
        role = user.role.code
        center_id = str(user.center_id) if user.center_id else ""
        phone = user.phone or ""
        student_id = ""
        teacher_id = ""
        if role == "student":
            from app.models.education import Student

            result = await session.execute(
                select(Student.id).where(Student.user_id == user.id, Student.deleted_at.is_(None))
            )
            sid = result.scalar_one_or_none()
            if sid:
                student_id = str(sid)
        if role == "teacher":
            from app.models.education import Teacher

            result = await session.execute(
                select(Teacher.id).where(Teacher.user_id == user.id, Teacher.deleted_at.is_(None))
            )
            tid = result.scalar_one_or_none()
            if tid:
                teacher_id = str(tid)
    else:
        role = "anonymous"
        center_id = ""
        phone = ""
        student_id = ""
        teacher_id = ""

    await session.execute(text("SELECT set_config('app.role', :role, true)"), {"role": role})
    await session.execute(text("SELECT set_config('app.center_id', :cid, true)"), {"cid": center_id})
    await session.execute(text("SELECT set_config('app.phone', :phone, true)"), {"phone": phone})
    await session.execute(text("SELECT set_config('app.student_id', :sid, true)"), {"sid": student_id})
    await session.execute(text("SELECT set_config('app.teacher_id', :tid, true)"), {"tid": teacher_id})
