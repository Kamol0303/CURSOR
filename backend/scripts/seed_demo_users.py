#!/usr/bin/env python3
"""Seed demo users for non-production environments only.

Usage:
  python -m scripts.seed_demo_users --i-understand-this-creates-demo-credentials
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import secrets
import sys
import uuid
from datetime import UTC, datetime

import pyotp
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

sys.path.insert(0, ".")

from app.core.config import settings
from app.core.permissions import ROLE_DEFINITIONS, ROLE_PERMISSIONS
from app.core.security import encrypt_totp_secret, hash_password
from app.models.identity import Permission, Role, RolePermission, TrainingCenter, User


DEMO_USERS = [
    ("super_admin", "admin.tamor", "Tamor#2026Admin!", True),
    ("hokimiyat_operator", "operator.hokimiyat", "Hokim#Op2026!", True),
    ("center_director", "director.aspect", "Direktor#2026!", True),
    ("center_admin", "admin.aspect", "CenterAdmin#26!", False),
    ("teacher", "teacher.dilnoza", "Teach#Dil2026!", False),
    ("auditor", "auditor.tuman", "Audit#Check26!", False),
]

PARENT_PHONE = "+998901234567"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed TaMoR demo users (non-production only)")
    parser.add_argument(
        "--i-understand-this-creates-demo-credentials",
        action="store_true",
        help="Required flag confirming you understand this creates demo credentials",
    )
    return parser.parse_args()


async def ensure_roles_and_permissions(session: AsyncSession) -> dict[str, Role]:
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

    return roles


async def seed() -> None:
    args = parse_args()
    if not args.i_understand_this_creates_demo_credentials:
        print("ERROR: Must pass --i-understand-this-creates-demo-credentials", file=sys.stderr)
        sys.exit(1)

    if settings.ENVIRONMENT == "production":
        print("ERROR: Refusing to run in production environment", file=sys.stderr)
        sys.exit(1)

    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        count_result = await session.execute(
            select(func.count()).select_from(User).where(User.is_demo_account.is_(False))
        )
        non_demo_count = count_result.scalar() or 0
        if non_demo_count > settings.SEED_NON_DEMO_USER_THRESHOLD:
            print(
                f"ERROR: Found {non_demo_count} non-demo users (threshold: {settings.SEED_NON_DEMO_USER_THRESHOLD})",
                file=sys.stderr,
            )
            sys.exit(1)

        roles = await ensure_roles_and_permissions(session)

        center_result = await session.execute(
            select(TrainingCenter).where(TrainingCenter.name == "Aspect Ta'lim Markazi")
        )
        center = center_result.scalar_one_or_none()
        if not center:
            center = TrainingCenter(
                name="Aspect Ta'lim Markazi",
                stir="123456789",
                director_name="Direktor Aspekt",
                phone="+998662123456",
                center_type="private",
                is_active=True,
            )
            session.add(center)
            await session.flush()

        print("\n" + "=" * 60)
        print("WARNING: DEMO CREDENTIALS — NON-PRODUCTION ONLY")
        print("=" * 60 + "\n")

        for role_code, username, password, mfa in DEMO_USERS:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    username=username,
                    password_hash=hash_password(password),
                    role_id=roles[role_code].id,
                    center_id=center.id if role_code in {"center_director", "center_admin", "teacher"} else None,
                    is_demo_account=True,
                    is_active=True,
                    password_changed_at=datetime.now(UTC),
                )
                session.add(user)
                await session.flush()

            if mfa:
                secret = pyotp.random_base32()
                user.mfa_enabled = True
                user.mfa_method = "totp"
                user.mfa_secret_encrypted = encrypt_totp_secret(secret)
                totp = pyotp.TOTP(secret)
                print(f"Role: {role_code}")
                print(f"  Username: {username}")
                print(f"  Password: {password}")
                print(f"  TOTP Secret: {secret}")
                print(f"  TOTP URI: {totp.provisioning_uri(name=username, issuer_name='TaMoR')}")
                print()
            else:
                print(f"Role: {role_code}")
                print(f"  Username: {username}")
                print(f"  Password: {password}")
                print()

        parent_role = roles["parent"]
        parent_result = await session.execute(select(User).where(User.phone == PARENT_PHONE))
        parent = parent_result.scalar_one_or_none()
        if not parent:
            parent = User(
                phone=PARENT_PHONE,
                role_id=parent_role.id,
                is_demo_account=True,
                is_active=True,
                locale_preference="uz",
            )
            session.add(parent)

        api_key = f"tamor_demo_sk_live_{secrets.token_hex(16)}"
        hmac_secret = secrets.token_hex(32)
        print("External API Consumer:")
        print(f"  API Key: {api_key}")
        print(f"  HMAC Secret: {hmac_secret}")
        print()
        print("Parent/Guardian:")
        print(f"  Phone: {PARENT_PHONE}")
        print("  OTP: logged to console in dev (no real SMS)")
        print("\n" + "=" * 60 + "\n")

        await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
