from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.schemas.grades import GradeCreate
from app.services import grade_service

router = APIRouter(prefix="/grades", tags=["grades"])


@router.get("", response_model=ApiResponse)
async def list_grades(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    student_id: UUID | None = None,
    user: User = Depends(requires_permission("grades.read")),
    db: AsyncSession = Depends(get_db),
):
    grades, total = await grade_service.list_grades(db, user, student_id=student_id, page=page, per_page=per_page)
    return ApiResponse(success=True, data=[g.model_dump() for g in grades], meta={"page": page, "per_page": per_page, "total": total})


@router.post("", response_model=ApiResponse, status_code=201)
async def create_grade(
    body: GradeCreate,
    user: User = Depends(requires_permission("grades.create")),
    db: AsyncSession = Depends(get_db),
):
    grade = await grade_service.create_grade(db, user, body)
    await db.commit()
    return ApiResponse(success=True, data=grade.model_dump())
