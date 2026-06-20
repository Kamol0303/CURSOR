from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/ratings")
async def download_ratings_report(
    request: Request,
    format: str = Query("pdf", pattern=r"^(pdf|excel)$"),
    locale: str = Query("uz", pattern=r"^(uz|ru|en)$"),
    user: User = Depends(requires_permission("reports.generate")),
    db: AsyncSession = Depends(get_db),
):
    file_format = "excel" if format == "excel" else "pdf"
    data, content_type, filename = await report_service.generate_ratings_report(
        db,
        user,
        file_format=file_format,
        locale=locale,
        ip_address=request.client.host if request.client else None,
    )
    return Response(
        content=data,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
