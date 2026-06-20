from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.security import hash_password
from app.main import app
from app.models import Base, MFAMethod, Role, User
from app.services.mfa import create_totp_secret, encrypt_totp_secret


@pytest_asyncio.fixture
async def session_factory(tmp_path) -> AsyncIterator[async_sessionmaker]:
    database_path = tmp_path / "test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    yield session_factory
    await engine.dispose()


@pytest_asyncio.fixture
async def seeded_db(session_factory: async_sessionmaker):
    async with session_factory() as session:
        super_role = Role(code="super_admin", name_uz="Admin", name_ru="Админ", name_en="Admin")
        parent_role = Role(code="parent", name_uz="Parent", name_ru="Родитель", name_en="Parent")
        session.add_all([super_role, parent_role])
        await session.flush()

        secret = create_totp_secret()
        admin = User(
            id=uuid.uuid4(),
            username="admin.tamor",
            email="admin@example.com",
            password_hash=hash_password("Tamor#2026Admin!"),
            role_id=super_role.id,
            locale_preference="uz",
            mfa_enabled=True,
            mfa_secret_encrypted=encrypt_totp_secret(secret),
            mfa_method=MFAMethod.totp,
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
            must_change_password=False,
            is_demo_account=True,
        )
        parent = User(
            id=uuid.uuid4(),
            phone="+998901234567",
            role_id=parent_role.id,
            locale_preference="uz",
            mfa_enabled=False,
            mfa_method=MFAMethod.none,
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
            must_change_password=False,
            is_demo_account=True,
        )
        session.add_all([admin, parent])
        await session.commit()
        return {"secret": secret, "admin_id": str(admin.id)}


@pytest_asyncio.fixture
async def client(session_factory: async_sessionmaker, seeded_db):
    async def override_get_db():
        async with session_factory() as session:
            yield session

    from app.core.database import get_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
    app.dependency_overrides.clear()
