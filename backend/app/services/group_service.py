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
    payload = data.model_dump(exclude_unset=True)
    if "teacher_id" in payload:
        await _validate_teacher_for_group(db, user, group, payload["teacher_id"])
    for key, value in payload.items():
        setattr(group, key, value)
    await db.flush()
    await db.refresh(group, ["subject", "teacher"])
    return group


async def assign_teacher_to_group(
    db: AsyncSession,
    user: User,
    group_id: UUID,
    teacher_id: UUID,
) -> Group:
    group = await get_group(db, user, group_id)
    if user.role.code not in {"super_admin", "center_director", "center_admin"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    await _validate_teacher_for_group(db, user, group, teacher_id)
    group.teacher_id = teacher_id
    await db.flush()
    await db.refresh(group, ["subject", "teacher"])
    return group


async def _validate_teacher_for_group(
    db: AsyncSession,
    user: User,
    group: Group,
    teacher_id: UUID | None,
) -> None:
    if teacher_id is None:
        return
    teacher = (
        await db.execute(
            select(Teacher).where(Teacher.id == teacher_id, Teacher.deleted_at.is_(None))
        )
    ).scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail={"code": "TEACHER_NOT_FOUND"})
    assert_center_access(user, teacher.center_id)
    if teacher.center_id != group.center_id:
        raise HTTPException(status_code=422, detail={"code": "CENTER_MISMATCH"})
    if not teacher.is_active:
        raise HTTPException(status_code=422, detail={"code": "TEACHER_INACTIVE"})


async def delete_group(db: AsyncSession, user: User, group_id: UUID) -> None:
    if user.role.code not in {"super_admin", "center_director"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    group = await get_group(db, user, group_id)
    from datetime import UTC, datetime

    group.deleted_at = datetime.now(UTC)


async def enroll_student(db: AsyncSession, user: User, group_id: UUID, student_id: UUID) -> Enrollment:
    group = await get_group(db, user, group_id)
    _assert_can_enroll(user)
    return await _enroll_one(db, user, group, student_id)


def _assert_can_enroll(user: User) -> None:
    if user.role.code not in {"super_admin", "center_director", "center_admin"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})


async def _enroll_one(db: AsyncSession, user: User, group: Group, student_id: UUID) -> Enrollment:
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
                Enrollment.group_id == group.id,
                Enrollment.student_id == student_id,
                Enrollment.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if existing:
        if existing.status != "active":
            existing.status = "active"
            await db.flush()
        return existing

    enrollment = Enrollment(
        student_id=student_id,
        group_id=group.id,
        center_id=group.center_id,
    )
    db.add(enrollment)
    await db.flush()
    return enrollment


async def enroll_students_batch(
    db: AsyncSession, user: User, group_id: UUID, student_ids: list[UUID]
) -> list[Enrollment]:
    group = await get_group(db, user, group_id)
    _assert_can_enroll(user)
    results: list[Enrollment] = []
    for student_id in student_ids:
        results.append(await _enroll_one(db, user, group, student_id))
    return results


async def list_group_enrollments(db: AsyncSession, user: User, group_id: UUID) -> list[dict]:
    group = await get_group(db, user, group_id)
    result = await db.execute(
        select(Enrollment, Student.full_name, Student.grade)
        .join(Student, Student.id == Enrollment.student_id)
        .where(
            Enrollment.group_id == group.id,
            Enrollment.status == "active",
            Enrollment.deleted_at.is_(None),
            Student.deleted_at.is_(None),
        )
        .order_by(Student.full_name)
    )
    return [
        {
            "enrollment_id": str(row[0].id),
            "student_id": str(row[0].student_id),
            "full_name": row[1],
            "grade": row[2],
        }
        for row in result.all()
    ]


async def unenroll_student(db: AsyncSession, user: User, group_id: UUID, student_id: UUID) -> None:
    group = await get_group(db, user, group_id)
    _assert_can_enroll(user)

    enrollment = (
        await db.execute(
            select(Enrollment).where(
                Enrollment.group_id == group.id,
                Enrollment.student_id == student_id,
                Enrollment.status == "active",
                Enrollment.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if not enrollment:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})

    from datetime import UTC, datetime

    enrollment.status = "inactive"
    enrollment.deleted_at = datetime.now(UTC)
    await db.flush()

