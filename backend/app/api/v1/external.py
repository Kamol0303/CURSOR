from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api_key_auth import require_api_scope
from app.core.database import get_db
from app.models.identity import ApiKey
from app.schemas.common import ApiResponse
from app.services import api_key_service

router = APIRouter(prefix="/external", tags=["external"])


@router.get("/aggregate-stats", response_model=ApiResponse)
async def aggregate_stats(
    api_key: ApiKey = Depends(require_api_scope("aggregate_stats.read")),
    db: AsyncSession = Depends(get_db),
):
    data = await api_key_service.get_aggregate_stats(db)
    return ApiResponse(success=True, data=data)
