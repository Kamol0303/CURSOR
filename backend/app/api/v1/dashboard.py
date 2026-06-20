from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis", response_model=ApiResponse)
async def get_kpis(
    user: User = Depends(requires_permission("dashboard.view")),
    db: AsyncSession = Depends(get_db),
):
    data = await dashboard_service.get_dashboard(db, user)
    return ApiResponse(success=True, data=data.model_dump())
