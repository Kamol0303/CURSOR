from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity import AuditLog


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
