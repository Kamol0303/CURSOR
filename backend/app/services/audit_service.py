from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.identity import AuditLog, User
from app.schemas.lesson_materials import AuditLogResponse


async def write_audit_log(
    db: AsyncSession,
    *,
    user_id: UUID | None,
    action: str,
    resource_type: str,
    resource_id: UUID | None = None,
    ip_address: str | None = None,
    details: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            details=details or {},
        )
    )


async def list_audit_logs(
    db: AsyncSession,
    *,
    page: int = 1,
    per_page: int = 50,
    action: str | None = None,
    resource_type: str | None = None,
    user_id: UUID | None = None,
) -> tuple[list[AuditLogResponse], int]:
    query = select(AuditLog).order_by(AuditLog.created_at.desc())
    if action:
        query = query.where(AuditLog.action.ilike(f"%{action}%"))
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    result = await db.execute(query.offset((page - 1) * per_page).limit(per_page))
    logs = list(result.scalars().all())

    user_ids = {log.user_id for log in logs if log.user_id}
    users_by_id: dict[UUID, User] = {}
    if user_ids:
        users_result = await db.execute(
            select(User).options(selectinload(User.role)).where(User.id.in_(user_ids))
        )
        users_by_id = {u.id: u for u in users_result.scalars().all()}

    responses: list[AuditLogResponse] = []
    for log in logs:
        user = users_by_id.get(log.user_id) if log.user_id else None
        responses.append(
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                username=user.username if user else None,
                user_role=user.role.code if user and user.role else None,
                action=log.action,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                details=log.details,
                ip_address=log.ip_address,
                created_at=log.created_at,
            )
        )
    return responses, total
