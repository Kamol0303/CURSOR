from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.schemas.subjects import SubjectCreate, SubjectUpdate
from app.services import subject_service

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=ApiResponse)
async def list_subjects(
    active_only: bool = Query(True),
    user: User = Depends(requires_permission("subjects.read")),
    db: AsyncSession = Depends(get_db),
):
    subjects = await subject_service.list_subjects(db, active_only=active_only)
    return ApiResponse(success=True, data=[s.model_dump() for s in subjects])


@router.get("/{subject_id}", response_model=ApiResponse)
async def get_subject(
    subject_id: UUID,
    user: User = Depends(requires_permission("subjects.read")),
    db: AsyncSession = Depends(get_db),
):
    subject = await subject_service.get_subject(db, subject_id)
    return ApiResponse(success=True, data=subject_service.subject_to_response(subject).model_dump())


@router.post("", response_model=ApiResponse, status_code=201)
async def create_subject(
    body: SubjectCreate,
    user: User = Depends(requires_permission("subjects.create")),
    db: AsyncSession = Depends(get_db),
):
    subject = await subject_service.create_subject(db, user, body)
    await db.commit()
    return ApiResponse(success=True, data=subject.model_dump())


@router.patch("/{subject_id}", response_model=ApiResponse)
async def update_subject(
    subject_id: UUID,
    body: SubjectUpdate,
    user: User = Depends(requires_permission("subjects.update")),
    db: AsyncSession = Depends(get_db),
):
    subject = await subject_service.update_subject(db, user, subject_id, body)
    await db.commit()
    return ApiResponse(success=True, data=subject.model_dump())


@router.delete("/{subject_id}", response_model=ApiResponse)
async def delete_subject(
    subject_id: UUID,
    user: User = Depends(requires_permission("subjects.delete")),
    db: AsyncSession = Depends(get_db),
):
    await subject_service.delete_subject(db, user, subject_id)
    await db.commit()
    return ApiResponse(success=True, data={"deleted": True})
