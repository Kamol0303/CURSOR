"""Shared fixtures for integration and security tests."""

from __future__ import annotations

import asyncio
import os
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.permissions import ROLE_DEFINITIONS, ROLE_PERMISSIONS
from app.core.pinfl import encrypt_pinfl
from app.core.rls import apply_rls_context, set_rls_role
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.education import Guardian, Student
from app.models.identity import Permission, Role, RolePermission, TrainingCenter, User


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: requires PostgreSQL and Redis")


async def _db_reachable() -> bool:
    try:
        engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def integration_available() -> bool:
    if os.getenv("ENVIRONMENT") not in {"test", "development", "ci"} and not os.getenv("DATABASE_URL"):
        return False
    return asyncio.run(_db_reachable())


@pytest_asyncio.fixture
async def db_session(integration_available) -> AsyncGenerator[AsyncSession, None]:
    if not integration_available:
        pytest.skip("PostgreSQL not available")

    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        set_rls_role("system")
        await apply_rls_context(session)
        yield session

    await engine.dispose()


async def _ensure_roles(session: AsyncSession) -> dict[str, Role]:
    roles: dict[str, Role] = {}
    for code, uz, ru, en in ROLE_DEFINITIONS:
        result = await session.execute(select(Role).where(Role.code == code))
        role = result.scalar_one_or_none()
        if not role:
            role = Role(code=code, name_uz=uz, name_ru=ru, name_en=en)
            session.add(role)
            await session.flush()
        roles[code] = role

    for role_code, perms in ROLE_PERMISSIONS.items():
        role = roles[role_code]
        for perm_code in perms:
            result = await session.execute(select(Permission).where(Permission.code == perm_code))
            perm = result.scalar_one_or_none()
            if not perm:
                module, action = perm_code.split(".", 1)
                perm = Permission(code=perm_code, module=module, action=action)
                session.add(perm)
                await session.flush()
            link = await session.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == perm.id,
                )
            )
            if not link.scalar_one_or_none():
                session.add(RolePermission(role_id=role.id, permission_id=perm.id))
    await session.commit()
    return roles


@pytest_asyncio.fixture
async def security_fixtures(db_session: AsyncSession) -> dict:
    roles = await _ensure_roles(db_session)
    suffix = uuid.uuid4().hex[:8]

    center_a = TrainingCenter(name=f"SecTest Center A {suffix}", is_active=True)
    center_b = TrainingCenter(name=f"SecTest Center B {suffix}", is_active=True)
    db_session.add_all([center_a, center_b])
    await db_session.flush()

    director_a = User(
        username=f"dir_a_{suffix}",
        password_hash=hash_password("Test#DirectorA1!"),
        role_id=roles["center_director"].id,
        center_id=center_a.id,
        is_active=True,
    )
    teacher_a = User(
        username=f"teacher_a_{suffix}",
        password_hash=hash_password("Test#TeacherA1!!"),
        role_id=roles["teacher"].id,
        center_id=center_a.id,
        is_active=True,
    )
    auditor = User(
        username=f"auditor_{suffix}",
        password_hash=hash_password("Test#Auditor1!!!"),
        role_id=roles["auditor"].id,
        is_active=True,
    )
    parent = User(
        phone=f"+998{int(suffix[:8], 16) % 1000000000:09d}",
        role_id=roles["parent"].id,
        is_active=True,
    )
    db_session.add_all([director_a, teacher_a, auditor, parent])
    await db_session.flush()

    student_a = Student(center_id=center_a.id, full_name="SecTest Student A", grade="9")
    student_b = Student(
        center_id=center_b.id,
        full_name="SecTest Student B",
        grade="10",
        jshshir_encrypted=encrypt_pinfl("12345678901234"),
    )
    db_session.add_all([student_a, student_b])
    await db_session.flush()

    db_session.add(Guardian(student_id=student_a.id, full_name="Parent A", phone=parent.phone))
    await db_session.commit()

    await db_session.refresh(director_a, attribute_names=["role"])
    await db_session.refresh(teacher_a, attribute_names=["role"])
    await db_session.refresh(auditor, attribute_names=["role"])
    await db_session.refresh(parent, attribute_names=["role"])

    def token_for(user: User) -> str:
        perms = ROLE_PERMISSIONS.get(user.role.code, [])
        access, _, _ = create_access_token(
            user_id=user.id,
            role=user.role.code,
            center_id=user.center_id,
            permissions=perms,
            locale="uz",
        )
        return access

    return {
        "center_a": center_a,
        "center_b": center_b,
        "director_a": director_a,
        "teacher_a": teacher_a,
        "auditor": auditor,
        "parent": parent,
        "student_a": student_a,
        "student_b": student_b,
        "token_director_a": token_for(director_a),
        "token_teacher_a": token_for(teacher_a),
        "token_auditor": token_for(auditor),
        "token_parent": token_for(parent),
    }


@pytest_asyncio.fixture
async def api_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
