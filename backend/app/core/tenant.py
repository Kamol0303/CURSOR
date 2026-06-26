"""Tenant isolation helpers — center, teacher-group, and parent-child scopes."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from app.models.education import Group, Student
    from app.models.identity import User

DISTRICT_WIDE_ROLES = frozenset({"super_admin", "hokimiyat_operator", "auditor"})
CENTER_SCOPED_ROLES = frozenset({"center_director", "center_admin", "teacher", "accountant"})

_tenant_context: ContextVar[TenantContext | None] = ContextVar("tenant_context", default=None)


@dataclass(frozen=True)
class TenantContext:
    user_id: UUID
    role: str
    center_id: UUID | None
    teacher_id: UUID | None = None
    parent_student_ids: tuple[UUID, ...] = ()

    @property
    def is_district_wide(self) -> bool:
        return self.role in DISTRICT_WIDE_ROLES


def set_tenant_context(ctx: TenantContext | None) -> None:
    _tenant_context.set(ctx)


def get_tenant_context() -> TenantContext:
    ctx = _tenant_context.get()
    if ctx is None:
        raise RuntimeError("Tenant context is not set")
    return ctx


def get_tenant_context_optional() -> TenantContext | None:
    return _tenant_context.get()


def clear_tenant_context() -> None:
    _tenant_context.set(None)


def assert_center_access(user: User, center_id: UUID) -> None:
    ctx = get_tenant_context_optional()
    if ctx and ctx.is_district_wide:
        return
    if user.role.code in DISTRICT_WIDE_ROLES:
        return
    if user.center_id != center_id:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})


def get_user_center_filter(user: User) -> UUID | None:
    """Returns center_id filter for scoped roles, None for district-wide access."""
    ctx = get_tenant_context_optional()
    if ctx:
        if ctx.is_district_wide:
            return None
        if ctx.role == "parent":
            return None
        return ctx.center_id

    if user.role.code in DISTRICT_WIDE_ROLES:
        return None
    if user.role.code == "parent":
        return None
    if user.center_id is None:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    return user.center_id


def can_modify_center(user: User, center_id: UUID) -> bool:
    if user.role.code == "super_admin":
        return True
    if user.role.code == "center_director" and user.center_id == center_id:
        return True
    return False


async def resolve_tenant_context(db: AsyncSession, user: User) -> TenantContext:
    from app.models.education import Guardian, Teacher

    teacher_id: UUID | None = None
    parent_student_ids: tuple[UUID, ...] = ()

    if user.role.code == "teacher":
        result = await db.execute(
            select(Teacher.id).where(
                Teacher.user_id == user.id,
                Teacher.deleted_at.is_(None),
            )
        )
        teacher_id = result.scalar_one_or_none()

    if user.role.code == "parent" and user.phone:
        result = await db.execute(
            select(Guardian.student_id).where(
                Guardian.phone == user.phone,
                Guardian.deleted_at.is_(None),
            )
        )
        parent_student_ids = tuple(row[0] for row in result.all())

    return TenantContext(
        user_id=user.id,
        role=user.role.code,
        center_id=user.center_id,
        teacher_id=teacher_id,
        parent_student_ids=parent_student_ids,
    )


def teacher_student_ids_subquery(teacher_id: UUID):
    from app.models.education import Enrollment, Group

    return (
        select(Enrollment.student_id)
        .join(Group, Group.id == Enrollment.group_id)
        .where(
            Group.teacher_id == teacher_id,
            Group.deleted_at.is_(None),
            Enrollment.status == "active",
            Enrollment.deleted_at.is_(None),
        )
        .distinct()
    )


def teacher_group_ids_subquery(teacher_id: UUID):
    from app.models.education import Group

    return select(Group.id).where(
        Group.teacher_id == teacher_id,
        Group.deleted_at.is_(None),
    )


def apply_student_list_scope(query: Select, ctx: TenantContext) -> Select:
    from app.models.education import Student

    if ctx.parent_student_ids:
        if not ctx.parent_student_ids:
            return query.where(Student.id.in_([]))
        return query.where(Student.id.in_(ctx.parent_student_ids))
    if ctx.role == "teacher":
        if not ctx.teacher_id:
            return query.where(Student.id.in_([]))
        return query.where(Student.id.in_(teacher_student_ids_subquery(ctx.teacher_id)))
    if ctx.center_id and not ctx.is_district_wide:
        return query.where(Student.center_id == ctx.center_id)
    return query


def apply_group_scope(query: Select, ctx: TenantContext, group_model) -> Select:
    if ctx.role == "teacher":
        if not ctx.teacher_id:
            return query.where(group_model.id.in_([]))
        return query.where(group_model.teacher_id == ctx.teacher_id)
    center_filter = None if ctx.is_district_wide else ctx.center_id
    if center_filter:
        return query.where(group_model.center_id == center_filter)
    return query


async def assert_student_in_scope(
    db: AsyncSession,
    ctx: TenantContext,
    student: Student,
) -> None:
    if ctx.is_district_wide:
        return
    if ctx.parent_student_ids:
        if student.id not in ctx.parent_student_ids:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
        return
    if ctx.role == "teacher":
        if not ctx.teacher_id:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
        from app.models.education import Enrollment, Group

        result = await db.execute(
            select(Enrollment.id)
            .join(Group, Group.id == Enrollment.group_id)
            .where(
                Enrollment.student_id == student.id,
                Group.teacher_id == ctx.teacher_id,
                Enrollment.status == "active",
                Enrollment.deleted_at.is_(None),
            )
            .limit(1)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
        return
    if ctx.center_id and student.center_id != ctx.center_id:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})


async def assert_group_in_scope(
    db: AsyncSession,
    ctx: TenantContext,
    group: Group,
    user: User,
) -> None:
    if ctx.is_district_wide:
        return
    if ctx.role == "teacher":
        if not ctx.teacher_id or group.teacher_id != ctx.teacher_id:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
        return
    assert_center_access(user, group.center_id)
