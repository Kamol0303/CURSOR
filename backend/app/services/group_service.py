from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.tenant import (
    assert_center_access,
    assert_group_in_scope,
    apply_group_scope,
    get_tenant_context_optional,
    resolve_tenant_context,
)
from app.models.education import Enrollment, Group, Student, Subject, Teacher
from app.models.identity import User
from app.schemas.groups import GroupCreate, GroupResponse, GroupUpdate


def group_to_response(group: Group, *, enrollment_count: int = 0) -> GroupResponse:
    subject_name = group.subject.name_uz if group.subject else None
    teacher_name = group.teacher.full_name if group.teacher else None
    return GroupResponse(
        id=group.id,
        center_id=group.center_id,
        subject_id=group.subject_id,
        name=group.name,
        teacher_id=group.teacher_id,
        room=group.room,
        schedule_json=group.schedule_json,
        start_date=group.start_date,
        end_date=group.end_date,
        is_active=group.is_active,
        enrollment_count=enrollment_count,
        subject_name_uz=subject_name,
        teacher_name=teacher_name,
    )


async def list_groups(
    db: AsyncSession,
    user: User,
    *,
    page: int = 1,
    per_page: int = 20,
    center_id: UUID | None = None,
) -> tuple[list[GroupResponse], int]:
    ctx = get_tenant_context_optional() or await resolve_tenant_context(db, user)
    query = (
        select(Group)
        .options(selectinload(Group.subject), selectinload(Group.teacher))
        .where(Group.deleted_at.is_(None))
    )
    query = apply_group_scope(query, ctx, Group)
    if ctx.is_district_wide and center_id:
        query = query.where(Group.center_id == center_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        query.order_by(Group.name).offset((page - 1) * per_page).limit(per_page)
    )
    groups = list(result.scalars().all())

    responses: list[GroupResponse] = []
    for group in groups:
        enroll_count = (
            await db.execute(
                select(func.count()).select_from(Enrollment).where(
                    Enrollment.group_id == group.id, Enrollment.status == "active"
                )
            )
        ).scalar() or 0
        responses.append(group_to_response(group, enrollment_count=enroll_count))
    return responses, total


async def get_group(db: AsyncSession, user: User, group_id: UUID) -> Group:
    result = await db.execute(
        select(Group)
        .options(selectinload(Group.subject), selectinload(Group.teacher), selectinload(Group.enrollments))
        .where(Group.id == group_id, Group.deleted_at.is_(None))
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    ctx = get_tenant_context_optional() or await resolve_tenant_context(db, user)
    await assert_group_in_scope(db, ctx, group, user)
    return group


async def create_group(db: AsyncSession, user: User, data: GroupCreate) -> Group:
    assert_center_access(user, data.center_id)
    if user.role.code not in {"super_admin", "center_director", "center_admin"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    group = Group(
        center_id=data.center_id,
        subject_id=data.subject_id,
        name=data.name,
        teacher_id=data.teacher_id,
        room=data.room,
        schedule_json=data.schedule_json,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    db.add(group)
    await db.flush()
    await db.refresh(group, ["subject", "teacher"])
    return group


async def update_group(db: AsyncSession, user: User, group_id: UUID, data: GroupUpdate) -> Group:
    group = await get_group(db, user, group_id)
    if user.role.code not in {"super_admin", "center_director", "center_admin"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(group, key, value)
    await db.flush()
    await db.refresh(group, ["subject", "teacher"])
    return group


async def delete_group(db: AsyncSession, user: User, group_id: UUID) -> None:
    if user.role.code not in {"super_admin", "center_director"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    group = await get_group(db, user, group_id)
    from datetime import UTC, datetime

    group.deleted_at = datetime.now(UTC)


async def enroll_student(db: AsyncSession, user: User, group_id: UUID, student_id: UUID) -> Enrollment:
    group = await get_group(db, user, group_id)
    if user.role.code not in {"super_admin", "center_director", "center_admin"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    student = (
        await db.execute(select(Student).where(Student.id == student_id, Student.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    assert_center_access(user, student.center_id)
    if student.center_id != group.center_id:
        raise HTTPException(status_code=422, detail={"code": "CENTER_MISMATCH"})

    existing = (
        await db.execute(
            select(Enrollment).where(
                Enrollment.group_id == group_id,
                Enrollment.student_id == student_id,
                Enrollment.status == "active",
            )
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    enrollment = Enrollment(
        student_id=student_id,
        group_id=group_id,
        center_id=group.center_id,
    )
    db.add(enrollment)
    await db.flush()
    return enrollment


async def list_subjects(db: AsyncSession) -> list[Subject]:
    result = await db.execute(select(Subject).where(Subject.is_active.is_(True)).order_by(Subject.name_uz))
    return list(result.scalars().all())
