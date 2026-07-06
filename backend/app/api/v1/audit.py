from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse, PaginationMeta
from app.services import audit_service

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=ApiResponse)
async def list_audit_logs(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    action: str | None = None,
    resource_type: str | None = None,
    user_id: UUID | None = None,
    user: User = Depends(requires_permission("audit.read")),
    db: AsyncSession = Depends(get_db),
):
    logs, total = await audit_service.list_audit_logs(
        db,
        page=page,
        per_page=per_page,
        action=action,
        resource_type=resource_type,
        user_id=user_id,
    )
    return ApiResponse(
        success=True,
        data=[log.model_dump() for log in logs],
        meta=PaginationMeta(page=page, per_page=per_page, total=total).model_dump(),
    )
