from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.services import rating_service

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.get("", response_model=ApiResponse)
async def list_ratings(
    limit: int = Query(10, ge=1, le=100),
    user: User = Depends(requires_permission("ratings.view")),
    db: AsyncSession = Depends(get_db),
):
    ratings = await rating_service.get_latest_ratings(db, limit=limit)
    data = [
        {
            "center_id": str(r.center_id),
            "center_name": r.center.name if r.center else "",
            "total_score": r.total_score,
            "rank": r.rank,
            "rank_change": r.rank_change,
            "criteria_breakdown": r.criteria_breakdown,
            "flagged_anomaly": r.flagged_anomaly,
            "period": r.period.isoformat(),
        }
        for r in ratings
    ]
    return ApiResponse(success=True, data=data)


@router.post("/compute", response_model=ApiResponse)
async def compute_ratings(
    user: User = Depends(requires_permission("system.settings")),
    db: AsyncSession = Depends(get_db),
):
    results = await rating_service.compute_ratings(db, user_id=user.id)
    return ApiResponse(success=True, data={"computed": len(results)})
