from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.schemas.teachers import TeacherCreate, TeacherUpdate
from app.services import teacher_service

router = APIRouter(prefix="/teachers", tags=["teachers"])


@router.get("", response_model=ApiResponse)
async def list_teachers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    center_id: UUID | None = None,
    search: str | None = None,
    user: User = Depends(requires_permission("teachers.read")),
    db: AsyncSession = Depends(get_db),
):
    teachers, total = await teacher_service.list_teachers(
        db, user, page=page, per_page=per_page, center_id=center_id, search=search
    )
    return ApiResponse(
        success=True,
        data=[teacher_service.teacher_to_response(t).model_dump() for t in teachers],
        meta={"page": page, "per_page": per_page, "total": total},
    )


@router.get("/{teacher_id}", response_model=ApiResponse)
async def get_teacher(
    teacher_id: UUID,
    user: User = Depends(requires_permission("teachers.read")),
    db: AsyncSession = Depends(get_db),
):
    teacher = await teacher_service.get_teacher(db, user, teacher_id)
    return ApiResponse(success=True, data=teacher_service.teacher_to_response(teacher).model_dump())


@router.post("", response_model=ApiResponse, status_code=201)
async def create_teacher(
    body: TeacherCreate,
    request: Request,
    user: User = Depends(requires_permission("teachers.create")),
    db: AsyncSession = Depends(get_db),
):
    teacher, credentials = await teacher_service.create_teacher(
        db,
        user,
        body,
        ip=request.client.host if request.client else None,
    )
    payload = {
        "teacher": teacher_service.teacher_to_response(teacher).model_dump(),
        "credentials": credentials,
    }
    return ApiResponse(success=True, data=payload)


@router.patch("/{teacher_id}", response_model=ApiResponse)
async def update_teacher(
    teacher_id: UUID,
    body: TeacherUpdate,
    user: User = Depends(requires_permission("teachers.update")),
    db: AsyncSession = Depends(get_db),
):
    teacher = await teacher_service.update_teacher(db, user, teacher_id, body)
    return ApiResponse(success=True, data=teacher_service.teacher_to_response(teacher).model_dump())


@router.delete("/{teacher_id}", response_model=ApiResponse)
async def delete_teacher(
    teacher_id: UUID,
    user: User = Depends(requires_permission("teachers.delete")),
    db: AsyncSession = Depends(get_db),
):
    await teacher_service.delete_teacher(db, user, teacher_id)
    return ApiResponse(success=True, data={"deleted": True})
