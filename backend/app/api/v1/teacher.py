from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.services import teacher_portal_service

router = APIRouter(prefix="/teacher", tags=["teacher-portal"])


def _require_teacher(user: User = Depends(get_current_user)) -> User:
    if user.role.code != "teacher":
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    return user


@router.get("/me", response_model=ApiResponse)
async def teacher_me(
    user: User = Depends(_require_teacher),
    db: AsyncSession = Depends(get_db),
):
    profile = await teacher_portal_service.get_teacher_profile(db, user)
    return ApiResponse(success=True, data=profile)


@router.get("/groups", response_model=ApiResponse)
async def teacher_groups(
    user: User = Depends(_require_teacher),
    db: AsyncSession = Depends(get_db),
):
    groups = await teacher_portal_service.list_teacher_groups(db, user)
    return ApiResponse(success=True, data=groups)


@router.get("/groups/{group_id}/students", response_model=ApiResponse)
async def teacher_group_students(
    group_id: UUID,
    user: User = Depends(_require_teacher),
    db: AsyncSession = Depends(get_db),
):
    students = await teacher_portal_service.get_group_students(db, user, group_id)
    return ApiResponse(success=True, data=students)


@router.get("/schedule", response_model=ApiResponse)
async def teacher_schedule(
    user: User = Depends(_require_teacher),
    db: AsyncSession = Depends(get_db),
):
    schedule = await teacher_portal_service.get_teacher_schedule(db, user)
    return ApiResponse(success=True, data=schedule)
