"""Read-only geography helpers for center (branch) assignment."""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.education import Mahalla, Region


async def list_regions(db: AsyncSession) -> list[Region]:
    result = await db.execute(
        select(Region).where(Region.deleted_at.is_(None)).order_by(Region.name_uz)
    )
    return list(result.scalars().all())


async def list_mahallas(db: AsyncSession, *, region_id: UUID | None = None) -> list[Mahalla]:
    query = select(Mahalla).where(Mahalla.deleted_at.is_(None))
    if region_id:
        query = query.where(Mahalla.region_id == region_id)
    result = await db.execute(query.order_by(Mahalla.name_uz))
    return list(result.scalars().all())


async def get_mahalla(db: AsyncSession, mahalla_id: UUID) -> Mahalla:
    result = await db.execute(
        select(Mahalla).where(Mahalla.id == mahalla_id, Mahalla.deleted_at.is_(None))
    )
    mahalla = result.scalar_one_or_none()
    if not mahalla:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    return mahalla
