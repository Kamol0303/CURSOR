from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.schemas.courses import CourseCreate, CourseUpdate, LessonCreate, LessonUpdate
from app.services import course_service

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=ApiResponse)
async def list_courses(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: User = Depends(requires_permission("courses.read")),
    db: AsyncSession = Depends(get_db),
):
    courses, total = await course_service.list_courses(db, user, page=page, per_page=per_page)
    return ApiResponse(
        success=True,
        data=[c.model_dump() for c in courses],
        meta={"page": page, "per_page": per_page, "total": total},
    )


@router.post("", response_model=ApiResponse, status_code=201)
async def create_course(
    body: CourseCreate,
    user: User = Depends(requires_permission("courses.create")),
    db: AsyncSession = Depends(get_db),
):
    course = await course_service.create_course(db, user, body)
    await db.commit()
    return ApiResponse(success=True, data=course.model_dump())


@router.patch("/{course_id}", response_model=ApiResponse)
async def update_course(
    course_id: UUID,
    body: CourseUpdate,
    user: User = Depends(requires_permission("courses.update")),
    db: AsyncSession = Depends(get_db),
):
    course = await course_service.update_course(db, user, course_id, body)
    await db.commit()
    return ApiResponse(success=True, data=course.model_dump())


@router.delete("/{course_id}", response_model=ApiResponse)
async def delete_course(
    course_id: UUID,
    user: User = Depends(requires_permission("courses.delete")),
    db: AsyncSession = Depends(get_db),
):
    await course_service.delete_course(db, user, course_id)
    await db.commit()
    return ApiResponse(success=True, data={"deleted": True})


@router.get("/{course_id}/lessons", response_model=ApiResponse)
async def list_lessons(
    course_id: UUID,
    user: User = Depends(requires_permission("courses.read")),
    db: AsyncSession = Depends(get_db),
):
    lessons = await course_service.list_lessons(db, user, course_id)
    return ApiResponse(success=True, data=[l.model_dump() for l in lessons])


@router.post("/{course_id}/lessons", response_model=ApiResponse, status_code=201)
async def create_lesson(
    course_id: UUID,
    body: LessonCreate,
    user: User = Depends(requires_permission("courses.update")),
    db: AsyncSession = Depends(get_db),
):
    lesson = await course_service.create_lesson(db, user, course_id, body)
    await db.commit()
    return ApiResponse(success=True, data=lesson.model_dump())


@router.patch("/{course_id}/lessons/{lesson_id}", response_model=ApiResponse)
async def update_lesson(
    course_id: UUID,
    lesson_id: UUID,
    body: LessonUpdate,
    user: User = Depends(requires_permission("courses.update")),
    db: AsyncSession = Depends(get_db),
):
    lesson = await course_service.update_lesson(db, user, course_id, lesson_id, body)
    await db.commit()
    return ApiResponse(success=True, data=lesson.model_dump())


@router.delete("/{course_id}/lessons/{lesson_id}", response_model=ApiResponse)
async def delete_lesson(
    course_id: UUID,
    lesson_id: UUID,
    user: User = Depends(requires_permission("courses.update")),
    db: AsyncSession = Depends(get_db),
):
    await course_service.delete_lesson(db, user, course_id, lesson_id)
    await db.commit()
    return ApiResponse(success=True, data={"deleted": True})
