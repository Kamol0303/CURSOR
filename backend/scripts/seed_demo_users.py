#!/usr/bin/env python3
"""
TaMoR Demo User Seed Script
============================
Creates demo accounts for all 8 roles in NON-PRODUCTION environments only.

Usage:
    cd backend && python -m scripts.seed_demo_users

WARNING: Never run this in production. All accounts are tagged is_demo_account=true.
"""

import asyncio
import hashlib
import secrets
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pyotp
import qrcode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.core.security import (
    encrypt_totp_secret,
    generate_backup_codes,
    hash_password,
    hash_token,
    is_valid_bcrypt_hash,
)
from app.models import ApiKey, ApiKeyScope, Mahalla, Permission, Region, Role, RolePermission, TrainingCenter, User

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║  ⚠️  TaMoR DEMO SEED SCRIPT — NON-PRODUCTION ONLY  ⚠️            ║
║  All accounts tagged is_demo_account=true                        ║
║  PURGE BEFORE PRODUCTION LAUNCH (see docs/security-architecture) ║
╚══════════════════════════════════════════════════════════════════╝
"""

ROLES = [
    ("super_admin", "Super administrator", "Суперадминистратор", "Super Administrator"),
    ("hokimiyat_operator", "Hokimiyat operatori", "Оператор хокимията", "Hokimiyat Operator"),
    ("center_director", "Markaz direktori", "Директор центра", "Center Director"),
    ("center_admin", "Markaz administratori", "Администратор центра", "Center Admin"),
    ("teacher", "O'qituvchi", "Учитель", "Teacher"),
    ("auditor", "Auditor", "Аудитор", "Auditor"),
    ("parent", "Ota-ona", "Родитель", "Parent/Guardian"),
    ("external_api", "Tashqi API", "Внешний API", "External API Consumer"),
]

PERMISSIONS = [
    ("centers.create", "centers", "create"),
    ("centers.read", "centers", "read"),
    ("centers.update", "centers", "update"),
    ("centers.delete", "centers", "delete"),
    ("students.create", "students", "create"),
    ("students.read", "students", "read"),
    ("students.update", "students", "update"),
    ("students.delete", "students", "delete"),
    ("ratings.view", "ratings", "view"),
    ("reports.generate", "reports", "generate"),
    ("settings.manage", "settings", "manage"),
    ("audit.view", "audit", "view"),
    ("audit.reveal_pinfl", "audit", "reveal_pinfl"),
    ("aggregate_stats.read", "aggregate_stats", "read"),
]

ROLE_PERMISSIONS = {
    "super_admin": [p[0] for p in PERMISSIONS],
    "hokimiyat_operator": [
        "centers.read", "students.read", "ratings.view", "reports.generate", "audit.view"
    ],
    "center_director": [
        "centers.read", "centers.update", "students.create", "students.read",
        "students.update", "students.delete", "ratings.view", "reports.generate",
    ],
    "center_admin": [
        "centers.read", "students.create", "students.read", "students.update", "ratings.view",
    ],
    "teacher": ["students.read", "ratings.view"],
    "auditor": [
        "centers.read", "students.read", "ratings.view", "reports.generate",
        "audit.view", "audit.reveal_pinfl",
    ],
    "parent": ["students.read", "ratings.view"],
    "external_api": ["aggregate_stats.read"],
}

DEMO_USERS = [
    {
        "username": "admin.tamor",
        "password": "Tamor#2026Admin!",
        "role": "super_admin",
        "mfa": True,
        "email": "admin@tamor.uz",
    },
    {
        "username": "operator.hokimiyat",
        "password": "Hokim#Op2026!",
        "role": "hokimiyat_operator",
        "mfa": True,
        "email": "operator@tamor.uz",
    },
    {
        "username": "director.aspect",
        "password": "Direktor#2026!",
        "role": "center_director",
        "mfa": True,
        "email": "director@aspect.uz",
        "center": True,
    },
    {
        "username": "admin.aspect",
        "password": "CenterAdmin#26!",
        "role": "center_admin",
        "mfa": False,
        "email": "admin@aspect.uz",
        "center": True,
    },
    {
        "username": "teacher.dilnoza",
        "password": "Teach#Dil2026!",
        "role": "teacher",
        "mfa": False,
        "email": "teacher@aspect.uz",
        "center": True,
    },
    {
        "username": "auditor.tuman",
        "password": "Audit#Check26!",
        "role": "auditor",
        "mfa": False,
        "email": "auditor@tamor.uz",
    },
    {
        "phone": "+998901234567",
        "role": "parent",
        "mfa": False,
    },
]


async def seed():
    if settings.is_production:
        print("FATAL: Cannot run seed script in production environment!")
        sys.exit(1)

    print(BANNER)

    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as db:
        role_map: dict[str, Role] = {}
        for code, uz, ru, en in ROLES:
            existing = await db.execute(select(Role).where(Role.code == code))
            role = existing.scalar_one_or_none()
            if not role:
                role = Role(code=code, name_uz=uz, name_ru=ru, name_en=en)
                db.add(role)
            role_map[code] = role
        await db.flush()

        perm_map: dict[str, Permission] = {}
        for code, module, action in PERMISSIONS:
            existing = await db.execute(select(Permission).where(Permission.code == code))
            perm = existing.scalar_one_or_none()
            if not perm:
                perm = Permission(code=code, module=module, action=action)
                db.add(perm)
            perm_map[code] = perm
        await db.flush()

        for role_code, perm_codes in ROLE_PERMISSIONS.items():
            role = role_map[role_code]
            for pc in perm_codes:
                existing = await db.execute(
                    select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == perm_map[pc].id,
                    )
                )
                if not existing.scalar_one_or_none():
                    db.add(RolePermission(role_id=role.id, permission_id=perm_map[pc].id))
        await db.flush()

        region_result = await db.execute(select(Region).where(Region.code == "SAM"))
        region = region_result.scalar_one_or_none()
        if not region:
            region = Region(
                name_uz="Samarqand viloyati",
                name_ru="Самаркандская область",
                name_en="Samarkand Region",
                code="SAM",
            )
            db.add(region)
            await db.flush()

        mahalla_result = await db.execute(
            select(Mahalla).where(Mahalla.name_uz == "Toyloq")
        )
        mahalla = mahalla_result.scalar_one_or_none()
        if not mahalla:
            mahalla = Mahalla(
                region_id=region.id,
                name_uz="Toyloq",
                name_ru="Тойлок",
                name_en="Toyloq",
            )
            db.add(mahalla)
            await db.flush()

        center_result = await db.execute(
            select(TrainingCenter).where(TrainingCenter.stir == "123456789")
        )
        center = center_result.scalar_one_or_none()
        if not center:
            center = TrainingCenter(
                name="Aspect Education Center",
                stir="123456789",
                director_name="Karimov Sardor",
                phone="+998901112233",
                email="info@aspect.uz",
                address="Toyloq tumani, Samarqand",
                mahalla_id=mahalla.id,
                license_number="LIC-2024-001",
                license_expiry=datetime.now(UTC) + timedelta(days=365),
                center_type="private",
                is_active=True,
                is_demo_data=True,
            )
            db.add(center)
            await db.flush()

        totp_secrets: dict[str, str] = {}

        for demo in DEMO_USERS:
            if "username" in demo:
                existing = await db.execute(
                    select(User).where(User.username == demo["username"])
                )
            else:
                existing = await db.execute(select(User).where(User.phone == demo["phone"]))

            user = existing.scalar_one_or_none()
            label = demo.get("username") or demo.get("phone")

            if user:
                if user.is_demo_account and "password" in demo:
                    was_invalid = not is_valid_bcrypt_hash(user.password_hash)
                    user.password_hash = hash_password(demo["password"])
                    user.failed_login_attempts = 0
                    user.is_locked = False
                    user.locked_until = None
                    user.password_changed_at = datetime.now(UTC)
                    action = "fixed" if was_invalid else "refreshed"
                    print(f"  [{action}] {label} — demo password hash")
                else:
                    print(f"  [skip] {label} already exists")
                continue

            role = role_map[demo["role"]]
            user = User(
                username=demo.get("username"),
                phone=demo.get("phone"),
                email=demo.get("email"),
                password_hash=hash_password(demo["password"]) if "password" in demo else None,
                role_id=role.id,
                center_id=center.id if demo.get("center") else None,
                locale_preference="uz",
                is_active=True,
                is_demo_account=True,
                password_changed_at=datetime.now(UTC),
            )

            if demo.get("mfa"):
                secret = pyotp.random_base32()
                user.mfa_enabled = True
                user.mfa_method = "totp"
                user.mfa_secret_encrypted = encrypt_totp_secret(secret)
                totp_secrets[demo["username"]] = secret

            db.add(user)
            await db.flush()

            if demo.get("mfa"):
                from app.models import MfaBackupCode
                for code in generate_backup_codes():
                    db.add(MfaBackupCode(user_id=user.id, code_hash=hash_password(code)))

            label = demo.get("username") or demo.get("phone")
            print(f"  [created] {label} ({demo['role']})")

        api_key_id = f"tamor_demo_{secrets.token_hex(8)}"
        hmac_secret = secrets.token_urlsafe(32)
        existing_key = await db.execute(
            select(ApiKey).where(ApiKey.is_demo_account.is_(True))
        )
        if not existing_key.scalar_one_or_none():
            api_key = ApiKey(
                key_id=api_key_id,
                key_hash=hash_token(api_key_id),
                hmac_secret_hash=hash_token(hmac_secret),
                is_active=True,
                is_demo_account=True,
            )
            db.add(api_key)
            await db.flush()
            db.add(ApiKeyScope(api_key_id=api_key.id, scope="aggregate_stats.read"))
            print(f"\n  [API Key] key_id: {api_key_id}")
            print(f"  [API Key] hmac_secret: {hmac_secret}")
            print("  [API Key] Scope: aggregate_stats.read, Rate: 10 req/min")

        await db.commit()

        print("\n" + "=" * 60)
        print("DEMO CREDENTIALS")
        print("=" * 60)
        print(f"{'Role':<22} {'Username/Phone':<25} {'Password':<20} {'MFA'}")
        print("-" * 60)
        for demo in DEMO_USERS:
            label = demo.get("username") or demo.get("phone", "")
            pwd = demo.get("password", "OTP (console)")
            mfa = "TOTP" if demo.get("mfa") else "—"
            print(f"{demo['role']:<22} {label:<25} {pwd:<20} {mfa}")

        print("\n" + "=" * 60)
        print("TOTP SECRETS (scan with Google Authenticator)")
        print("=" * 60)
        for username, secret in totp_secrets.items():
            totp = pyotp.TOTP(secret)
            uri = totp.provisioning_uri(name=username, issuer_name="TaMoR")
            print(f"\n  {username}:")
            print(f"    Secret: {secret}")
            print(f"    URI: {uri}")
            try:
                qr = qrcode.QRCode(version=1, box_size=1, border=1)
                qr.add_data(uri)
                qr.make(fit=True)
                qr.print_ascii(invert=True)
            except Exception:
                pass

        print("\n✅ Seed complete. Parent OTP is logged to console in dev mode.")


if __name__ == "__main__":
    asyncio.run(seed())
