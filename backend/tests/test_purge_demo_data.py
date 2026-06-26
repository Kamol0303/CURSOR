"""Tests for demo data purge script."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.core.security import hash_password
from app.models.identity import Role, TrainingCenter, User
from scripts.purge_demo_data import collect_counts, purge_demo_rows


@pytest.mark.asyncio
async def test_purge_removes_demo_entities(db_session, monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    role = (await db_session.execute(select(Role).where(Role.code == "center_admin"))).scalar_one_or_none()
    if not role:
        role = Role(code="center_admin", name_uz="Admin", name_ru="Admin", name_en="Admin")
        db_session.add(role)
        await db_session.flush()

    center = TrainingCenter(
        name="Demo Purge Center",
        stir="999999999",
        director_name="Test",
        phone="+998900000000",
        center_type="private",
        is_active=True,
        is_demo_data=True,
    )
    db_session.add(center)
    await db_session.flush()

    user = User(
        username="purge.test.demo",
        password_hash=hash_password("Test#12345!"),
        role_id=role.id,
        center_id=center.id,
        is_demo_account=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    before = await collect_counts(db_session)
    assert before["demo_users"] >= 1
    assert before["demo_centers"] >= 1

    await purge_demo_rows(db_session)
    await db_session.commit()

    remaining_users = (
        await db_session.execute(select(func.count()).select_from(User).where(User.is_demo_account.is_(True)))
    ).scalar()
    remaining_centers = (
        await db_session.execute(
            select(func.count()).select_from(TrainingCenter).where(TrainingCenter.is_demo_data.is_(True))
        )
    ).scalar()

    assert remaining_users == 0 or before["demo_users"] - remaining_users >= 1
    assert remaining_centers == 0 or before["demo_centers"] - remaining_centers >= 1
