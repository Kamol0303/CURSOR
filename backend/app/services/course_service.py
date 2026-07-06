from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.tenant import assert_center_access, get_user_center_filter
from app.models.academics import Course, Lesson
from app.models.education import Subject
from app.models.identity import User
from app.schemas.courses import CourseCreate, CourseResponse, CourseUpdate, LessonCreate, LessonResponse, LessonUpdate
from app.services.audit_service import write_audit_log


def course_to_response(course: Course, *, lesson_count: int | None = None) -> CourseResponse:
    count = lesson_count if lesson_count is not None else len(course.lessons)
    subject_name = course.subject.name_uz if course.subject else None
    return CourseResponse(
        id=course.id,
        center_id=course.center_id,
        subject_id=course.subject_id,
        name=course.name,
        description=course.description,
        price=course.price,
        duration_weeks=course.duration_weeks,
        is_active=course.is_active,
        lesson_count=count,
        subject_name_uz=subject_name,
    )


def lesson_to_response(lesson: Lesson) -> LessonResponse:
    return LessonResponse(
        id=lesson.id,
        course_id=lesson.course_id,
        center_id=lesson.center_id,
        title=lesson.title,
        scheduled_at=lesson.scheduled_at,
        duration_minutes=lesson.duration_minutes,
        room=lesson.room,
        group_id=lesson.group_id,
    )


async def list_courses(
    db: AsyncSession,
    user: User,
    *,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[CourseResponse], int]:
    center_filter = get_user_center_filter(user)
    query = select(Course).where(Course.deleted_at.is_(None))
    if center_filter:
        query = query.where(Course.center_id == center_filter)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    result = await db.execute(
        query.options(selectinload(Course.lessons), selectinload(Course.subject))
        .order_by(Course.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    courses = list(result.scalars().all())
    return [course_to_response(c) for c in courses], total


async def get_course(db: AsyncSession, user: User, course_id: UUID) -> Course:
    result = await db.execute(
        select(Course)
        .options(selectinload(Course.lessons), selectinload(Course.subject))
        .where(Course.id == course_id, Course.deleted_at.is_(None))
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    assert_center_access(user, course.center_id)
    return course


async def create_course(db: AsyncSession, user: User, body: CourseCreate) -> CourseResponse:
    center_id = body.center_id or user.center_id
    if not center_id:
        raise HTTPException(status_code=422, detail={"code": "CENTER_REQUIRED"})
    assert_center_access(user, center_id)

    subject = (
        await db.execute(select(Subject).where(Subject.id == body.subject_id, Subject.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail={"code": "SUBJECT_NOT_FOUND"})

    course = Course(
        center_id=center_id,
        subject_id=body.subject_id,
        name=body.name,
        description=body.description,
        price=body.price,
        duration_weeks=body.duration_weeks,
    )
    db.add(course)
    await db.flush()
    course.subject = subject
    await write_audit_log(
        db,
        user_id=user.id,
        action="course.create",
        resource_type="course",
        resource_id=course.id,
        details={"name": course.name, "subject_id": str(course.subject_id)},
    )
    return course_to_response(course)


async def update_course(db: AsyncSession, user: User, course_id: UUID, body: CourseUpdate) -> CourseResponse:
    course = await get_course(db, user, course_id)
    data = body.model_dump(exclude_unset=True)
    if "subject_id" in data and data["subject_id"] is not None:
        subject = (
            await db.execute(
                select(Subject).where(Subject.id == data["subject_id"], Subject.deleted_at.is_(None))
            )
        ).scalar_one_or_none()
        if not subject:
            raise HTTPException(status_code=404, detail={"code": "SUBJECT_NOT_FOUND"})
        course.subject = subject
    for key, value in data.items():
        setattr(course, key, value)
    await db.flush()
    await write_audit_log(
        db,
        user_id=user.id,
        action="course.update",
        resource_type="course",
        resource_id=course.id,
        details={"changed_fields": list(data.keys())},
    )
    return course_to_response(course)


async def delete_course(db: AsyncSession, user: User, course_id: UUID) -> None:
    from datetime import UTC, datetime

    course = await get_course(db, user, course_id)
    course.deleted_at = datetime.now(UTC)
    await write_audit_log(
        db,
        user_id=user.id,
        action="course.delete",
        resource_type="course",
        resource_id=course.id,
        details={"name": course.name},
    )


async def list_lessons(db: AsyncSession, user: User, course_id: UUID) -> list[LessonResponse]:
    course = await get_course(db, user, course_id)
    result = await db.execute(
        select(Lesson)
        .where(Lesson.course_id == course.id, Lesson.deleted_at.is_(None))
        .order_by(Lesson.scheduled_at.asc().nullslast(), Lesson.created_at.asc())
    )
    return [lesson_to_response(l) for l in result.scalars().all()]


async def create_lesson(db: AsyncSession, user: User, course_id: UUID, body: LessonCreate) -> LessonResponse:
    course = await get_course(db, user, course_id)
    lesson = Lesson(
        course_id=course.id,
        center_id=course.center_id,
        title=body.title,
        scheduled_at=body.scheduled_at,
        duration_minutes=body.duration_minutes,
        room=body.room,
        group_id=body.group_id,
    )
    db.add(lesson)
    await db.flush()
    await write_audit_log(
        db,
        user_id=user.id,
        action="lesson.create",
        resource_type="lesson",
        resource_id=lesson.id,
        details={"title": lesson.title, "course_id": str(course.id)},
    )
    return lesson_to_response(lesson)


async def update_lesson(
    db: AsyncSession, user: User, course_id: UUID, lesson_id: UUID, body: LessonUpdate
) -> LessonResponse:
    await get_course(db, user, course_id)
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.course_id == course_id, Lesson.deleted_at.is_(None))
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    assert_center_access(user, lesson.center_id)
    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(lesson, key, value)
    await db.flush()
    await write_audit_log(
        db,
        user_id=user.id,
        action="lesson.update",
        resource_type="lesson",
        resource_id=lesson.id,
        details={"changed_fields": list(data.keys())},
    )
    return lesson_to_response(lesson)


async def delete_lesson(db: AsyncSession, user: User, course_id: UUID, lesson_id: UUID) -> None:
    from datetime import UTC, datetime

    await get_course(db, user, course_id)
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.course_id == course_id, Lesson.deleted_at.is_(None))
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    assert_center_access(user, lesson.center_id)
    lesson.deleted_at = datetime.now(UTC)
    await write_audit_log(
        db,
        user_id=user.id,
        action="lesson.delete",
        resource_type="lesson",
        resource_id=lesson.id,
        details={"title": lesson.title},
    )
