from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.services import student_service

router = APIRouter(prefix="/student", tags=["student"])


def _require_student(user: User) -> None:
    if user.role.code != "student":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})


@router.get("/me", response_model=ApiResponse)
async def student_me(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_student(user)
    profile = await student_service.get_student_profile(db, user)
    return ApiResponse(success=True, data=profile)


@router.get("/grades", response_model=ApiResponse)
async def student_grades(
    user: User = Depends(requires_permission("grades.read")),
    db: AsyncSession = Depends(get_db),
):
    _require_student(user)
    data = await student_service.get_student_grades(db, user)
    return ApiResponse(success=True, data=data)


@router.get("/exams", response_model=ApiResponse)
async def student_exams(
    user: User = Depends(requires_permission("exams.read")),
    db: AsyncSession = Depends(get_db),
):
    _require_student(user)
    data = await student_service.get_student_exams(db, user)
    return ApiResponse(success=True, data=data)


@router.get("/exam-results", response_model=ApiResponse)
async def student_exam_results(
    user: User = Depends(requires_permission("exams.read")),
    db: AsyncSession = Depends(get_db),
):
    _require_student(user)
    data = await student_service.get_student_exam_results(db, user)
    return ApiResponse(success=True, data=data)


@router.get("/attendance", response_model=ApiResponse)
async def student_attendance(
    user: User = Depends(requires_permission("attendance.read")),
    db: AsyncSession = Depends(get_db),
):
    _require_student(user)
    data = await student_service.get_student_attendance(db, user)
    return ApiResponse(success=True, data=data)


@router.get("/enrollments", response_model=ApiResponse)
async def student_enrollments(
    user: User = Depends(requires_permission("students.read")),
    db: AsyncSession = Depends(get_db),
):
    _require_student(user)
    data = await student_service.get_student_enrollments(db, user)
    return ApiResponse(success=True, data=data)
