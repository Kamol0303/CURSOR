from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academics import Course, Exam, Grade
from app.models.education import Group, Subject, TeacherSubject
from app.models.identity import User
from app.models.ratings_certs import Certificate
from app.schemas.subjects import SubjectCreate, SubjectResponse, SubjectUpdate


def subject_to_response(subject: Subject) -> SubjectResponse:
    return SubjectResponse(
        id=subject.id,
        name_uz=subject.name_uz,
        name_ru=subject.name_ru,
        name_en=subject.name_en,
        is_active=subject.is_active,
    )


async def list_subjects(
    db: AsyncSession,
    *,
    active_only: bool = True,
) -> list[SubjectResponse]:
    query = select(Subject).where(Subject.deleted_at.is_(None))
    if active_only:
        query = query.where(Subject.is_active.is_(True))
    result = await db.execute(query.order_by(Subject.name_uz))
    return [subject_to_response(s) for s in result.scalars().all()]


async def get_subject(db: AsyncSession, subject_id: UUID) -> Subject:
    result = await db.execute(
        select(Subject).where(Subject.id == subject_id, Subject.deleted_at.is_(None))
    )
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    return subject


async def create_subject(db: AsyncSession, user: User, body: SubjectCreate) -> SubjectResponse:
    if user.role.code != "super_admin":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    subject = Subject(
        name_uz=body.name_uz,
        name_ru=body.name_ru,
        name_en=body.name_en,
        is_active=body.is_active,
    )
    db.add(subject)
    await db.flush()
    return subject_to_response(subject)


async def update_subject(
    db: AsyncSession,
    user: User,
    subject_id: UUID,
    body: SubjectUpdate,
) -> SubjectResponse:
    if user.role.code != "super_admin":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    subject = await get_subject(db, subject_id)
    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(subject, key, value)
    await db.flush()
    return subject_to_response(subject)


async def _assert_subject_deletable(db: AsyncSession, subject_id: UUID) -> None:
    checks: list[tuple] = [
        (Group, Group.subject_id == subject_id, Group.deleted_at.is_(None)),
        (Course, Course.subject_id == subject_id, Course.deleted_at.is_(None)),
        (Exam, Exam.subject_id == subject_id, Exam.deleted_at.is_(None)),
        (Grade, Grade.subject_id == subject_id, Grade.deleted_at.is_(None)),
        (TeacherSubject, TeacherSubject.subject_id == subject_id, True),
        (Certificate, Certificate.subject_id == subject_id, Certificate.deleted_at.is_(None)),
    ]
    for model, subject_filter, active_filter in checks:
        query = select(func.count()).select_from(model).where(subject_filter)
        if active_filter is not True:
            query = query.where(active_filter)
        count = (await db.execute(query)).scalar() or 0
        if count > 0:
            raise HTTPException(status_code=409, detail={"code": "SUBJECT_IN_USE"})


async def delete_subject(db: AsyncSession, user: User, subject_id: UUID) -> None:
    if user.role.code != "super_admin":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    subject = await get_subject(db, subject_id)
    await _assert_subject_deletable(db, subject_id)
    subject.deleted_at = datetime.now(UTC)
    subject.is_active = False
    await db.flush()
