from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.common import ApiResponse
from app.services import parent_service

router = APIRouter(prefix="/parent", tags=["parent"])


@router.get("/children", response_model=ApiResponse)
async def list_children(
    user: User = Depends(requires_permission("students.read")),
    db: AsyncSession = Depends(get_db),
):
    if user.role.code != "parent":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    children = await parent_service.get_children_for_parent(db, user)
    data = [
        {
            "id": str(c.id),
            "full_name": c.full_name,
            "grade": c.grade,
            "school": c.school,
            "center_name": c.center.name if c.center else "",
            "certificates_count": len(c.certificates),
        }
        for c in children
    ]
    return ApiResponse(success=True, data=data)


@router.get("/children/{student_id}/certificates", response_model=ApiResponse)
async def list_child_certificates(
    student_id: UUID,
    user: User = Depends(requires_permission("certificates.read")),
    db: AsyncSession = Depends(get_db),
):
    if user.role.code != "parent":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    certs = await parent_service.get_child_certificates(db, user, student_id)
    locale = user.locale_preference or "uz"
    data = [
        {
            "id": str(c.id),
            "certificate_number": c.certificate_number,
            "course_name": getattr(c, f"course_name_{locale}", c.course_name_uz),
            "issue_date": c.issue_date.isoformat(),
            "status": c.status,
            "file_id": str(c.file_id) if c.file_id else None,
        }
        for c in certs
    ]
    return ApiResponse(success=True, data=data)
