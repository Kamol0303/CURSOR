from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.schemas.students import StudentCreate, StudentUpdate
from app.services import student_service

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=ApiResponse)
async def list_students(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    center_id: UUID | None = None,
    user: User = Depends(requires_permission("students.read")),
    db: AsyncSession = Depends(get_db),
):
    students, total = await student_service.list_students(
        db, user, page=page, per_page=per_page, center_id=center_id
    )
    return ApiResponse(
        success=True,
        data=[student_service.student_to_response(s).model_dump() for s in students],
        meta={"page": page, "per_page": per_page, "total": total},
    )


@router.get("/{student_id}", response_model=ApiResponse)
async def get_student(
    student_id: UUID,
    user: User = Depends(requires_permission("students.read")),
    db: AsyncSession = Depends(get_db),
):
    student = await student_service.get_student(db, user, student_id)
    return ApiResponse(success=True, data=student_service.student_to_response(student).model_dump())


@router.post("", response_model=ApiResponse, status_code=201)
async def create_student(
    body: StudentCreate,
    user: User = Depends(requires_permission("students.create")),
    db: AsyncSession = Depends(get_db),
):
    student = await student_service.create_student(db, user, body)
    return ApiResponse(success=True, data=student_service.student_to_response(student).model_dump())


@router.patch("/{student_id}", response_model=ApiResponse)
async def update_student(
    student_id: UUID,
    body: StudentUpdate,
    user: User = Depends(requires_permission("students.update")),
    db: AsyncSession = Depends(get_db),
):
    student = await student_service.update_student(db, user, student_id, body)
    return ApiResponse(success=True, data=student_service.student_to_response(student).model_dump())


@router.delete("/{student_id}", response_model=ApiResponse)
async def delete_student(
    student_id: UUID,
    user: User = Depends(requires_permission("students.delete")),
    db: AsyncSession = Depends(get_db),
):
    await student_service.delete_student(db, user, student_id)
    return ApiResponse(success=True, data={"deleted": True})


@router.post("/{student_id}/reveal-pinfl", response_model=ApiResponse)
async def reveal_pinfl(
    student_id: UUID,
    request: Request,
    user: User = Depends(requires_permission("pinfl.reveal")),
    db: AsyncSession = Depends(get_db),
):
    pinfl = await student_service.reveal_pinfl(
        db,
        user,
        student_id,
        ip_address=request.client.host if request.client else None,
    )
    return ApiResponse(success=True, data={"jshshir": pinfl})
