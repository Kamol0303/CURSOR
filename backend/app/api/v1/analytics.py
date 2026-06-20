from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/insights", response_model=ApiResponse)
async def get_insights(
    user: User = Depends(requires_permission("analytics.view")),
    db: AsyncSession = Depends(get_db),
):
    predictions = await analytics_service.get_latest_predictions(db)
    log = await analytics_service.get_latest_analysis_log(db)
    data = {
        "predictions": [analytics_service.serialize_prediction(p) for p in predictions],
        "last_run": {
            "run_id": str(log.run_id),
            "status": log.status,
            "metrics_count": log.metrics_count,
            "duration_ms": log.duration_ms,
            "created_at": log.created_at.isoformat(),
        }
        if log
        else None,
    }
    return ApiResponse(success=True, data=data)


@router.post("/run", response_model=ApiResponse)
async def run_analytics(
    request: Request,
    user: User = Depends(requires_permission("system.settings")),
    db: AsyncSession = Depends(get_db),
):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"code": "NOT_AUTHENTICATED"})
    try:
        result = await analytics_service.trigger_analytics_run(auth_header.split(" ", 1)[1])
        count = await analytics_service.store_predictions_from_run(db, result)
        await db.commit()
        return ApiResponse(success=True, data={"predictions_stored": count, "run_id": result.get("run_id")})
    except Exception as exc:
        raise HTTPException(status_code=502, detail={"code": "ANALYTICS_SERVICE_ERROR", "message": str(exc)}) from exc
