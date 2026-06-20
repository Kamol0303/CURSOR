from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rls import apply_rls_context, set_rls_role
from app.schemas.common import ApiResponse
from app.services import certificate_service

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/verify/{certificate_number}", response_model=ApiResponse)
async def verify_certificate(
    certificate_number: str,
    request: Request,
    locale: str = Query("uz", pattern=r"^(uz|ru|en)$"),
    db: AsyncSession = Depends(get_db),
):
    set_rls_role("verifier")
    await apply_rls_context(db)
    result = await certificate_service.verify_certificate_public(
        db,
        certificate_number,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        locale=locale,
    )
    return ApiResponse(success=True, data=result)
