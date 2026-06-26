import hashlib
import secrets
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant import (
    assert_group_in_scope,
    get_tenant_context_optional,
    resolve_tenant_context,
)
from app.models.education import Group, Student
from app.models.identity import User
from app.models.operations import AttendanceRecord, AttendanceSession
from app.schemas.attendance import AttendanceMarkRequest, AttendanceRecordResponse


def record_to_response(record: AttendanceRecord, student_name: str | None = None) -> AttendanceRecordResponse:
    return AttendanceRecordResponse(
        id=record.id,
        student_id=record.student_id,
        group_id=record.group_id,
        session_date=record.session_date,
        status=record.status,
        method=record.method,
        student_name=student_name,
    )


async def _load_group(db: AsyncSession, user: User, group_id: UUID) -> Group:
    group = (
        await db.execute(select(Group).where(Group.id == group_id, Group.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    ctx = get_tenant_context_optional() or await resolve_tenant_context(db, user)
    await assert_group_in_scope(db, ctx, group, user)
    return group


async def mark_attendance(
    db: AsyncSession, user: User, data: AttendanceMarkRequest, *, method: str = "manual"
) -> AttendanceRecord:
    group = await _load_group(db, user, data.group_id)

    student = (
        await db.execute(select(Student).where(Student.id == data.student_id, Student.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if not student or student.center_id != group.center_id:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})

    existing = (
        await db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.student_id == data.student_id,
                AttendanceRecord.group_id == data.group_id,
                AttendanceRecord.session_date == data.session_date,
            )
        )
    ).scalar_one_or_none()

    if existing:
        existing.status = data.status
        existing.method = method
        existing.marked_by = user.id
        existing.notes = data.notes
        await db.flush()
        return existing

    record = AttendanceRecord(
        student_id=data.student_id,
        group_id=data.group_id,
        center_id=group.center_id,
        session_date=data.session_date,
        status=data.status,
        method=method,
        marked_by=user.id,
        notes=data.notes,
    )
    db.add(record)
    await db.flush()
    return record


async def list_attendance(
    db: AsyncSession,
    user: User,
    *,
    group_id: UUID,
    session_date: date,
) -> list[AttendanceRecordResponse]:
    await _load_group(db, user, group_id)

    result = await db.execute(
        select(AttendanceRecord, Student.full_name)
        .join(Student, Student.id == AttendanceRecord.student_id)
        .where(AttendanceRecord.group_id == group_id, AttendanceRecord.session_date == session_date)
        .order_by(Student.full_name)
    )
    return [record_to_response(row[0], student_name=row[1]) for row in result.all()]


async def create_qr_session(
    db: AsyncSession, user: User, *, group_id: UUID, session_date: date
) -> tuple[AttendanceSession, str]:
    group = await _load_group(db, user, group_id)

    token = secrets.token_urlsafe(24)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = datetime.now(UTC) + timedelta(minutes=15)

    session = AttendanceSession(
        group_id=group_id,
        center_id=group.center_id,
        session_date=session_date,
        qr_token_hash=token_hash,
        expires_at=expires_at,
        created_by=user.id,
    )
    db.add(session)
    await db.flush()

    qr_payload = f"TMB-ATT:{group_id}:{session_date.isoformat()}:{token}"
    return session, qr_payload


async def mark_via_qr(
    db: AsyncSession,
    user: User,
    *,
    qr_payload: str,
    student_id: UUID,
) -> AttendanceRecord:
    parts = qr_payload.split(":")
    if len(parts) != 5 or parts[0] != "TMB-ATT":
        raise HTTPException(status_code=422, detail={"code": "INVALID_QR"})

    group_id = UUID(parts[1])
    session_date = date.fromisoformat(parts[2])
    token = parts[4]
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    session = (
        await db.execute(
            select(AttendanceSession).where(
                AttendanceSession.group_id == group_id,
                AttendanceSession.session_date == session_date,
                AttendanceSession.qr_token_hash == token_hash,
            )
        )
    ).scalar_one_or_none()
    if not session or session.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=422, detail={"code": "QR_EXPIRED"})

    return await mark_attendance(
        db,
        user,
        AttendanceMarkRequest(
            student_id=student_id,
            group_id=group_id,
            session_date=session_date,
            status="present",
        ),
        method="qr",
    )


async def attendance_summary(
    db: AsyncSession, user: User, *, group_id: UUID, month: str
) -> dict:
    await _load_group(db, user, group_id)

    year, mon = map(int, month.split("-"))
    start = date(year, mon, 1)
    end = date(year + 1, 1, 1) if mon == 12 else date(year, mon + 1, 1)

    result = await db.execute(
        select(AttendanceRecord.status, func.count())
        .where(
            AttendanceRecord.group_id == group_id,
            AttendanceRecord.session_date >= start,
            AttendanceRecord.session_date < end,
        )
        .group_by(AttendanceRecord.status)
    )
    counts = {row[0]: row[1] for row in result.all()}
    return {"group_id": str(group_id), "month": month, "by_status": counts}
