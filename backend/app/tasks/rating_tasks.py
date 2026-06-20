"""Celery tasks for scheduled background jobs."""

from __future__ import annotations

import asyncio

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.rating_tasks.compute_ratings_daily")
def compute_ratings_daily() -> dict:
    return asyncio.run(_compute_ratings())


async def _compute_ratings() -> dict:
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.core.config import settings
    from app.core.rls import set_rls_role
    from app.core.rls import apply_rls_context
    from app.services import rating_service

    set_rls_role("system")
    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        await apply_rls_context(session)
        results = await rating_service.compute_ratings(session)
        await session.commit()

    await engine.dispose()
    return {"computed": len(results)}
