from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.centers import CenterCreate, CenterResponse, CenterUpdate
from app.schemas.common import ApiResponse
from app.services import center_service

router = APIRouter(prefix="/centers", tags=["centers"])


@router.get("", response_model=ApiResponse)
async def list_centers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: User = Depends(requires_permission("centers.read")),
    db: AsyncSession = Depends(get_db),
):
    centers, total = await center_service.list_centers(db, user, page=page, per_page=per_page)
    return ApiResponse(
        success=True,
        data=[CenterResponse.model_validate(c).model_dump() for c in centers],
        meta={"page": page, "per_page": per_page, "total": total},
    )


@router.get("/{center_id}", response_model=ApiResponse)
async def get_center(
    center_id: UUID,
    user: User = Depends(requires_permission("centers.read")),
    db: AsyncSession = Depends(get_db),
):
    center = await center_service.get_center(db, user, center_id)
    return ApiResponse(success=True, data=CenterResponse.model_validate(center).model_dump())


@router.post("", response_model=ApiResponse, status_code=201)
async def create_center(
    body: CenterCreate,
    user: User = Depends(requires_permission("centers.create")),
    db: AsyncSession = Depends(get_db),
):
    center = await center_service.create_center(db, user, body)
    return ApiResponse(success=True, data=CenterResponse.model_validate(center).model_dump())


@router.patch("/{center_id}", response_model=ApiResponse)
async def update_center(
    center_id: UUID,
    body: CenterUpdate,
    user: User = Depends(requires_permission("centers.update")),
    db: AsyncSession = Depends(get_db),
):
    center = await center_service.update_center(db, user, center_id, body)
    return ApiResponse(success=True, data=CenterResponse.model_validate(center).model_dump())


@router.delete("/{center_id}", response_model=ApiResponse)
async def delete_center(
    center_id: UUID,
    user: User = Depends(requires_permission("centers.delete")),
    db: AsyncSession = Depends(get_db),
):
    await center_service.delete_center(db, user, center_id)
    return ApiResponse(success=True, data={"deleted": True})
