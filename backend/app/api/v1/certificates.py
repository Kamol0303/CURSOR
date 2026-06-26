from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.services import certificate_service

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get("", response_model=ApiResponse)
async def list_certificates(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: User = Depends(requires_permission("ratings.view")),
    db: AsyncSession = Depends(get_db),
):
    certs, total = await certificate_service.list_certificates(db, user, page=page, per_page=per_page)
    data = [
        {
            "id": str(c.id),
            "certificate_number": c.certificate_number,
            "student_name": c.student.full_name if c.student else "",
            "center_name": c.center.name if c.center else "",
            "course_name": c.course_name_uz,
            "issue_date": c.issue_date.isoformat(),
            "status": c.status,
            "qr_base64": certificate_service.generate_qr_base64(c.certificate_number),
        }
        for c in certs
    ]
    return ApiResponse(success=True, data=data, meta={"page": page, "per_page": per_page, "total": total})


@router.post("/issue", response_model=ApiResponse, status_code=201)
async def issue_certificate(
    request: Request,
    student_id: UUID = Query(...),
    subject_id: UUID | None = Query(None),
    user: User = Depends(requires_permission("students.update")),
    db: AsyncSession = Depends(get_db),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
):
    cert = await certificate_service.issue_certificate(
        db,
        user,
        student_id=student_id,
        subject_id=subject_id,
        idempotency_key=idempotency_key,
        ip_address=request.client.host if request.client else None,
    )
    return ApiResponse(
        success=True,
        data={
            "id": str(cert.id),
            "certificate_number": cert.certificate_number,
            "issue_date": cert.issue_date.isoformat(),
            "qr_base64": certificate_service.generate_qr_base64(cert.certificate_number),
            "integrity_hash": cert.integrity_hash,
        },
    )
