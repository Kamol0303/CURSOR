from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.centers import (
    CenterCreate,
    CenterOnboardCreate,
    CenterOnboardResponse,
    CenterProfileComplete,
    CenterResponse,
    CenterUpdate,
)
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
        data=[center_service.center_to_response(c) for c in centers],
        meta={"page": page, "per_page": per_page, "total": total},
    )


@router.get("/{center_id}", response_model=ApiResponse)
async def get_center(
    center_id: UUID,
    user: User = Depends(requires_permission("centers.read")),
    db: AsyncSession = Depends(get_db),
):
    center = await center_service.get_center(db, user, center_id)
    return ApiResponse(success=True, data=center_service.center_to_response(center))


@router.post("/onboard", response_model=ApiResponse, status_code=201)
async def onboard_center(
    body: CenterOnboardCreate,
    request: Request,
    user: User = Depends(requires_permission("centers.create")),
    db: AsyncSession = Depends(get_db),
):
    center, _director, temp_password = await center_service.onboard_center(
        db,
        user,
        body,
        ip_address=request.client.host if request.client else None,
    )
    payload = CenterOnboardResponse(
        center=CenterResponse.model_validate(center),
        director_username=body.director_username,
        temporary_password=temp_password,
    )
    await db.refresh(center, ["mahalla"])
    payload_dict = payload.model_dump()
    payload_dict["center"] = center_service.center_to_response(center)
    return ApiResponse(success=True, data=payload_dict)


@router.get("/onboarding/status", response_model=ApiResponse)
async def onboarding_status(
    user: User = Depends(requires_permission("centers.read")),
    db: AsyncSession = Depends(get_db),
):
    status = await center_service.get_onboarding_status(db, user)
    return ApiResponse(success=True, data=status)


@router.post("/onboarding/complete", response_model=ApiResponse)
async def complete_onboarding(
    body: CenterProfileComplete,
    user: User = Depends(requires_permission("centers.update")),
    db: AsyncSession = Depends(get_db),
):
    center = await center_service.complete_center_profile(db, user, body)
    await db.refresh(center, ["mahalla"])
    return ApiResponse(success=True, data=center_service.center_to_response(center))


@router.post("", response_model=ApiResponse, status_code=201)
async def create_center(
    body: CenterCreate,
    user: User = Depends(requires_permission("centers.create")),
    db: AsyncSession = Depends(get_db),
):
    center = await center_service.create_center(db, user, body)
    await db.refresh(center, ["mahalla"])
    return ApiResponse(success=True, data=center_service.center_to_response(center))


@router.patch("/{center_id}", response_model=ApiResponse)
async def update_center(
    center_id: UUID,
    body: CenterUpdate,
    user: User = Depends(requires_permission("centers.update")),
    db: AsyncSession = Depends(get_db),
):
    center = await center_service.update_center(db, user, center_id, body)
    await db.refresh(center, ["mahalla"])
    return ApiResponse(success=True, data=center_service.center_to_response(center))


@router.delete("/{center_id}", response_model=ApiResponse)
async def delete_center(
    center_id: UUID,
    user: User = Depends(requires_permission("centers.delete")),
    db: AsyncSession = Depends(get_db),
):
    await center_service.delete_center(db, user, center_id)
    return ApiResponse(success=True, data={"deleted": True})
