from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.core.tenant import assert_center_access, get_user_center_filter
from app.models.academics import Grade
from app.models.education import Student
from app.models.identity import User
from app.schemas.grades import GradeCreate, GradeResponse

logger = get_logger(__name__)


async def list_grades(
    db: AsyncSession,
    user: User,
    *,
    student_id: UUID | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[GradeResponse], int]:
    center_filter = get_user_center_filter(user)
    query = select(Grade).where(Grade.deleted_at.is_(None))
    if center_filter:
        query = query.where(Grade.center_id == center_filter)
    if student_id:
        query = query.where(Grade.student_id == student_id)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    result = await db.execute(query.order_by(Grade.graded_at.desc()).offset((page - 1) * per_page).limit(per_page))
    grades = list(result.scalars().all())
    return [_to_response(g) for g in grades], total


async def create_grade(db: AsyncSession, user: User, body: GradeCreate) -> GradeResponse:
    center_id = body.center_id or user.center_id
    if not center_id:
        raise HTTPException(status_code=422, detail={"code": "CENTER_REQUIRED"})
    assert_center_access(user, center_id)

    student = await db.get(Student, body.student_id)
    if not student or student.deleted_at:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND"})

    grade = Grade(
        student_id=body.student_id,
        subject_id=body.subject_id,
        group_id=body.group_id,
        center_id=center_id,
        grade_value=body.grade_value,
        grade_type=body.grade_type,
        term=body.term,
        notes=body.notes,
        graded_by=user.id,
    )
    db.add(grade)
    await db.flush()
    logger.info("grade_created grade_id=%s student_id=%s value=%s", grade.id, body.student_id, body.grade_value)
    return _to_response(grade)


def _to_response(grade: Grade) -> GradeResponse:
    return GradeResponse(
        id=grade.id,
        student_id=grade.student_id,
        subject_id=grade.subject_id,
        group_id=grade.group_id,
        center_id=grade.center_id,
        grade_value=grade.grade_value,
        grade_type=grade.grade_type,
        term=grade.term,
        notes=grade.notes,
        graded_at=grade.graded_at,
    )
