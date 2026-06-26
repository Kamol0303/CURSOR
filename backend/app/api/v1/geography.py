from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.services import geography_service

router = APIRouter(tags=["geography"])


@router.get("/regions", response_model=ApiResponse)
async def list_regions(
    user: User = Depends(requires_permission("centers.read")),
    db: AsyncSession = Depends(get_db),
):
    regions = await geography_service.list_regions(db)
    return ApiResponse(
        success=True,
        data=[
            {"id": str(r.id), "name_uz": r.name_uz, "name_ru": r.name_ru, "name_en": r.name_en}
            for r in regions
        ],
    )


@router.get("/mahallas", response_model=ApiResponse)
async def list_mahallas(
    region_id: UUID | None = Query(None),
    user: User = Depends(requires_permission("centers.read")),
    db: AsyncSession = Depends(get_db),
):
    mahallas = await geography_service.list_mahallas(db, region_id=region_id)
    return ApiResponse(
        success=True,
        data=[
            {
                "id": str(m.id),
                "region_id": str(m.region_id),
                "name_uz": m.name_uz,
                "name_ru": m.name_ru,
                "name_en": m.name_en,
            }
            for m in mahallas
        ],
    )
