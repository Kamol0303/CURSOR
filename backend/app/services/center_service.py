from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant import assert_center_access, can_modify_center, get_user_center_filter
from app.models.identity import TrainingCenter, User
from app.schemas.centers import CenterCreate, CenterUpdate


async def list_centers(
    db: AsyncSession,
    user: User,
    *,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[TrainingCenter], int]:
    center_filter = get_user_center_filter(user)
    query = select(TrainingCenter).where(TrainingCenter.deleted_at.is_(None))
    if center_filter:
        query = query.where(TrainingCenter.id == center_filter)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    result = await db.execute(
        query.order_by(TrainingCenter.name).offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total


async def get_center(db: AsyncSession, user: User, center_id: UUID) -> TrainingCenter:
    result = await db.execute(
        select(TrainingCenter).where(TrainingCenter.id == center_id, TrainingCenter.deleted_at.is_(None))
    )
    center = result.scalar_one_or_none()
    if not center:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    assert_center_access(user, center.id)
    return center


async def create_center(db: AsyncSession, user: User, data: CenterCreate) -> TrainingCenter:
    if user.role.code != "super_admin":
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    center = TrainingCenter(**data.model_dump())
    db.add(center)
    await db.flush()
    return center


async def update_center(
    db: AsyncSession, user: User, center_id: UUID, data: CenterUpdate
) -> TrainingCenter:
    center = await get_center(db, user, center_id)
    if not can_modify_center(user, center_id):
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(center, key, value)
    await db.flush()
    return center


async def delete_center(db: AsyncSession, user: User, center_id: UUID) -> None:
    if user.role.code != "super_admin":
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    center = await get_center(db, user, center_id)
    from datetime import UTC, datetime

    center.deleted_at = datetime.now(UTC)
    center.is_active = False
