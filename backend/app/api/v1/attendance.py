from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import requires_permission
from app.models.identity import User
from app.schemas.attendance import AttendanceMarkRequest, AttendanceSessionResponse, QrScanRequest
from app.schemas.common import ApiResponse
from app.services import attendance_service

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("", response_model=ApiResponse)
async def list_attendance(
    group_id: UUID,
    session_date: date,
    user: User = Depends(requires_permission("attendance.read")),
    db: AsyncSession = Depends(get_db),
):
    records = await attendance_service.list_attendance(db, user, group_id=group_id, session_date=session_date)
    return ApiResponse(success=True, data=[r.model_dump() for r in records])


@router.post("/mark", response_model=ApiResponse)
async def mark_attendance(
    body: AttendanceMarkRequest,
    user: User = Depends(requires_permission("attendance.mark")),
    db: AsyncSession = Depends(get_db),
):
    record = await attendance_service.mark_attendance(db, user, body)
    return ApiResponse(success=True, data={"id": str(record.id), "status": record.status})


@router.post("/qr-session", response_model=ApiResponse)
async def create_qr_session(
    group_id: UUID,
    session_date: date,
    user: User = Depends(requires_permission("attendance.mark")),
    db: AsyncSession = Depends(get_db),
):
    session, qr_payload = await attendance_service.create_qr_session(
        db, user, group_id=group_id, session_date=session_date
    )
    return ApiResponse(
        success=True,
        data=AttendanceSessionResponse(
            id=session.id,
            group_id=session.group_id,
            session_date=session.session_date,
            qr_payload=qr_payload,
            expires_at=session.expires_at.isoformat(),
        ).model_dump(),
    )


@router.post("/qr-scan", response_model=ApiResponse)
async def qr_scan(
    body: QrScanRequest,
    user: User = Depends(requires_permission("attendance.mark")),
    db: AsyncSession = Depends(get_db),
):
    record = await attendance_service.mark_via_qr(
        db, user, qr_payload=body.qr_payload, student_id=body.student_id
    )
    return ApiResponse(success=True, data={"id": str(record.id), "status": record.status})


@router.get("/summary", response_model=ApiResponse)
async def attendance_summary(
    group_id: UUID,
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    user: User = Depends(requires_permission("attendance.read")),
    db: AsyncSession = Depends(get_db),
):
    data = await attendance_service.attendance_summary(db, user, group_id=group_id, month=month)
    return ApiResponse(success=True, data=data)
