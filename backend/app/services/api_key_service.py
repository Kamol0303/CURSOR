"""API key lookup and external aggregate statistics."""

from __future__ import annotations

import secrets
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_token
from app.models.education import Student, Teacher
from app.models.identity import ApiKey, ApiKeyScope, TrainingCenter


async def find_active_api_key(db: AsyncSession, raw_key: str) -> ApiKey | None:
    key_hash = hash_token(raw_key)
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.key_hash == key_hash,
            ApiKey.is_active.is_(True),
            ApiKey.revoked_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def get_api_key_scopes(db: AsyncSession, api_key_id: UUID) -> set[str]:
    result = await db.execute(select(ApiKeyScope.scope).where(ApiKeyScope.api_key_id == api_key_id))
    return {row[0] for row in result.all()}


async def create_api_key(
    db: AsyncSession,
    *,
    scopes: list[str],
    label_prefix: str = "tmb",
) -> tuple[str, ApiKey]:
    raw_key = f"{label_prefix}_sk_live_{secrets.token_hex(16)}"
    hmac_secret = secrets.token_hex(32)
    api_key = ApiKey(
        key_prefix=raw_key[:12],
        key_hash=hash_token(raw_key),
        hmac_secret_hash=hash_token(hmac_secret),
        is_active=True,
    )
    db.add(api_key)
    await db.flush()
    for scope in scopes:
        db.add(ApiKeyScope(api_key_id=api_key.id, scope=scope))
    await db.flush()
    return raw_key, api_key


async def get_aggregate_stats(db: AsyncSession) -> dict:
    centers = (await db.execute(
        select(func.count()).select_from(TrainingCenter).where(TrainingCenter.deleted_at.is_(None))
    )).scalar() or 0
    students = (await db.execute(
        select(func.count()).select_from(Student).where(Student.deleted_at.is_(None))
    )).scalar() or 0
    teachers = (await db.execute(
        select(func.count()).select_from(Teacher).where(Teacher.deleted_at.is_(None))
    )).scalar() or 0
    active_centers = (await db.execute(
        select(func.count())
        .select_from(TrainingCenter)
        .where(TrainingCenter.deleted_at.is_(None), TrainingCenter.is_active.is_(True))
    )).scalar() or 0
    return {
        "total_centers": centers,
        "active_centers": active_centers,
        "total_students": students,
        "total_teachers": teachers,
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
    }
