from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.schemas.exams import ExamCreate, ExamSubmitRequest, ExamUpdate
from app.services import exam_service

router = APIRouter(prefix="/exams", tags=["exams"])


@router.get("", response_model=ApiResponse)
async def list_exams(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: User = Depends(requires_permission("exams.read")),
    db: AsyncSession = Depends(get_db),
):
    exams, total = await exam_service.list_exams(db, user, page=page, per_page=per_page)
    return ApiResponse(success=True, data=[e.model_dump() for e in exams], meta={"page": page, "per_page": per_page, "total": total})


@router.post("", response_model=ApiResponse, status_code=201)
async def create_exam(
    body: ExamCreate,
    user: User = Depends(requires_permission("exams.create")),
    db: AsyncSession = Depends(get_db),
):
    exam = await exam_service.create_exam(db, user, body)
    await db.commit()
    return ApiResponse(success=True, data=exam.model_dump())


@router.patch("/{exam_id}", response_model=ApiResponse)
async def update_exam(
    exam_id: UUID,
    body: ExamUpdate,
    user: User = Depends(requires_permission("exams.update")),
    db: AsyncSession = Depends(get_db),
):
    exam = await exam_service.update_exam(db, user, exam_id, body)
    await db.commit()
    return ApiResponse(success=True, data=exam.model_dump())


@router.post("/{exam_id}/submit", response_model=ApiResponse)
async def submit_exam(
    exam_id: UUID,
    body: ExamSubmitRequest,
    user: User = Depends(requires_permission("exams.submit")),
    db: AsyncSession = Depends(get_db),
):
    result = await exam_service.submit_exam(db, user, exam_id, body)
    await db.commit()
    return ApiResponse(success=True, data=result.model_dump())


@router.get("/{exam_id}/results", response_model=ApiResponse)
async def list_exam_results(
    exam_id: UUID,
    user: User = Depends(requires_permission("exams.read")),
    db: AsyncSession = Depends(get_db),
):
    results = await exam_service.list_results(db, user, exam_id)
    return ApiResponse(success=True, data=[r.model_dump() for r in results])
