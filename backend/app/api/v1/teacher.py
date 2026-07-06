from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.identity import User
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.lesson_materials import LessonGenerateRequest
from app.services import lesson_generation_service

router = APIRouter(prefix="/teacher", tags=["teacher-portal"])


def _require_teacher(user: User = Depends(get_current_user)) -> User:
    if user.role.code != "teacher":
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    return user


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


@router.get("/me", response_model=ApiResponse)
async def teacher_me(
    user: User = Depends(_require_teacher),
    db: AsyncSession = Depends(get_db),
):
    from app.services import teacher_portal_service

    profile = await teacher_portal_service.get_teacher_profile(db, user)
    return ApiResponse(success=True, data=profile)


@router.get("/groups", response_model=ApiResponse)
async def teacher_groups(
    user: User = Depends(_require_teacher),
    db: AsyncSession = Depends(get_db),
):
    from app.services import teacher_portal_service

    groups = await teacher_portal_service.list_teacher_groups(db, user)
    return ApiResponse(success=True, data=groups)


@router.get("/groups/{group_id}/students", response_model=ApiResponse)
async def teacher_group_students(
    group_id: UUID,
    user: User = Depends(_require_teacher),
    db: AsyncSession = Depends(get_db),
):
    from app.services import teacher_portal_service

    students = await teacher_portal_service.get_group_students(db, user, group_id)
    return ApiResponse(success=True, data=students)


@router.get("/schedule", response_model=ApiResponse)
async def teacher_schedule(
    user: User = Depends(_require_teacher),
    db: AsyncSession = Depends(get_db),
):
    from app.services import teacher_portal_service

    schedule = await teacher_portal_service.get_teacher_schedule(db, user)
    return ApiResponse(success=True, data=schedule)


@router.get("/subjects", response_model=ApiResponse)
async def teacher_subjects(
    user: User = Depends(_require_teacher),
    db: AsyncSession = Depends(get_db),
):
    subjects = await lesson_generation_service.list_teacher_subjects(db, user)
    return ApiResponse(success=True, data=subjects)


@router.get("/lesson-materials", response_model=ApiResponse)
async def teacher_lesson_materials(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: User = Depends(_require_teacher),
    db: AsyncSession = Depends(get_db),
):
    materials, total = await lesson_generation_service.list_teacher_materials(
        db, user, page=page, per_page=per_page
    )
    return ApiResponse(
        success=True,
        data=[m.model_dump() for m in materials],
        meta=PaginationMeta(page=page, per_page=per_page, total=total).model_dump(),
    )


@router.post("/lesson-materials/generate", response_model=ApiResponse)
async def teacher_generate_lesson(
    request: Request,
    body: LessonGenerateRequest,
    user: User = Depends(_require_teacher),
    db: AsyncSession = Depends(get_db),
):
    material = await lesson_generation_service.generate_lesson_material(
        db, user, body, ip_address=_client_ip(request)
    )
    return ApiResponse(success=True, data=material.model_dump())


@router.post("/lesson-materials/{material_id}/start", response_model=ApiResponse)
async def teacher_start_lesson(
    request: Request,
    material_id: UUID,
    user: User = Depends(_require_teacher),
    db: AsyncSession = Depends(get_db),
):
    material = await lesson_generation_service.start_lesson_material(
        db, user, material_id, ip_address=_client_ip(request)
    )
    return ApiResponse(success=True, data=material.model_dump())
