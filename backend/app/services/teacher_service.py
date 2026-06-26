from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.tenant import assert_center_access, get_user_center_filter
from app.models.education import Teacher, TeacherSubject
from app.models.identity import User
from app.schemas.teachers import TeacherCreate, TeacherResponse, TeacherUpdate


def teacher_to_response(teacher: Teacher) -> TeacherResponse:
    subject_ids = [ts.subject_id for ts in teacher.teacher_subjects]
    return TeacherResponse(
        id=teacher.id,
        center_id=teacher.center_id,
        full_name=teacher.full_name,
        phone=teacher.phone,
        specialization=teacher.specialization,
        years_of_experience=teacher.years_of_experience,
        start_date=teacher.start_date,
        is_active=teacher.is_active,
        subject_ids=subject_ids,
    )


async def list_teachers(
    db: AsyncSession,
    user: User,
    *,
    page: int = 1,
    per_page: int = 20,
    center_id: UUID | None = None,
    search: str | None = None,
) -> tuple[list[Teacher], int]:
    center_filter = get_user_center_filter(user)
    query = (
        select(Teacher)
        .options(selectinload(Teacher.teacher_subjects))
        .where(Teacher.deleted_at.is_(None), Teacher.is_active.is_(True))
    )
    if center_filter:
        query = query.where(Teacher.center_id == center_filter)
    elif center_id:
        query = query.where(Teacher.center_id == center_id)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(
            Teacher.full_name.ilike(pattern)
            | Teacher.phone.ilike(pattern)
            | Teacher.specialization.ilike(pattern)
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        query.order_by(Teacher.full_name).offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total


async def get_teacher(db: AsyncSession, user: User, teacher_id: UUID) -> Teacher:
    result = await db.execute(
        select(Teacher)
        .options(selectinload(Teacher.teacher_subjects))
        .where(Teacher.id == teacher_id, Teacher.deleted_at.is_(None))
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    assert_center_access(user, teacher.center_id)
    return teacher


async def create_teacher(
    db: AsyncSession,
    user: User,
    data: TeacherCreate,
    *,
    ip: str | None = None,
) -> tuple[Teacher, dict | None]:
    assert_center_access(user, data.center_id)
    if user.role.code not in {"super_admin", "center_director"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    teacher = Teacher(
        center_id=data.center_id,
        full_name=data.full_name,
        phone=data.phone,
        specialization=data.specialization,
        years_of_experience=data.years_of_experience,
        start_date=data.start_date,
    )
    db.add(teacher)
    await db.flush()

    for subject_id in data.subject_ids:
        db.add(TeacherSubject(teacher_id=teacher.id, subject_id=subject_id))

    credentials_info = None
    from app.services.credential_service import provision_teacher_account

    credentials_info = await provision_teacher_account(
        db,
        user,
        teacher=teacher,
        full_name=data.full_name,
        phone=data.phone,
        ip=ip,
    )

    await db.refresh(teacher, ["teacher_subjects"])
    return teacher, credentials_info


async def update_teacher(
    db: AsyncSession, user: User, teacher_id: UUID, data: TeacherUpdate
) -> Teacher:
    teacher = await get_teacher(db, user, teacher_id)
    if user.role.code not in {"super_admin", "center_director"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    for key, value in data.model_dump(exclude_unset=True, exclude={"subject_ids"}).items():
        setattr(teacher, key, value)

    if data.subject_ids is not None:
        for ts in list(teacher.teacher_subjects):
            await db.delete(ts)
        for subject_id in data.subject_ids:
            db.add(TeacherSubject(teacher_id=teacher.id, subject_id=subject_id))

    await db.flush()
    await db.refresh(teacher, ["teacher_subjects"])
    return teacher


async def delete_teacher(db: AsyncSession, user: User, teacher_id: UUID) -> None:
    if user.role.code not in {"super_admin", "center_director"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    teacher = await get_teacher(db, user, teacher_id)
    teacher.deleted_at = datetime.now(UTC)
    teacher.is_active = False
