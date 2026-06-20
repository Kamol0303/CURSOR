from __future__ import annotations

import os
import secrets
from datetime import datetime, timezone

import qrcode
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import encrypt_value, hash_password, hash_secret
from app.models import (
    APIKey,
    APIKeyScope,
    Base,
    MFARecoveryCode,
    MFAMethod,
    PasswordHistory,
    Permission,
    Role,
    RolePermission,
    TrainingCenter,
    User,
)
from app.services.mfa import create_totp_secret, encrypt_totp_secret, generate_recovery_codes, provisioning_uri


settings = get_settings()

ROLE_DEFINITIONS = [
    ("super_admin", "Super Admin", "Супер админ", "Super Admin"),
    ("hokimiyat_operator", "Hokimiyat operatori", "Оператор хокимията", "Hokimiyat Operator"),
    ("center_director", "Markaz direktori", "Директор центра", "Center Director"),
    ("center_admin", "Markaz administratori", "Администратор центра", "Center Admin"),
    ("teacher", "O'qituvchi", "Преподаватель", "Teacher"),
    ("auditor", "Auditor", "Аудитор", "Auditor"),
    ("parent", "Ota-ona", "Родитель", "Parent/Guardian"),
    ("external_api_consumer", "Tashqi API iste'molchisi", "Внешний API клиент", "External API Consumer"),
]

PERMISSIONS = [
    ("centers.create", "centers", "create"),
    ("centers.view", "centers", "view"),
    ("students.create", "students", "create"),
    ("students.view", "students", "view"),
    ("ratings.view", "ratings", "view"),
    ("reports.generate", "reports", "generate"),
    ("system_settings.manage", "system_settings", "manage"),
    ("audit_logs.view", "audit_logs", "view"),
    ("pinfl.reveal", "pinfl", "reveal"),
    ("aggregate_stats.read", "aggregate_stats", "read"),
]

ROLE_PERMISSION_MAP = {
    "super_admin": {
        "centers.create",
        "centers.view",
        "students.create",
        "students.view",
        "ratings.view",
        "reports.generate",
        "system_settings.manage",
        "audit_logs.view",
    },
    "hokimiyat_operator": {"centers.view", "students.view", "ratings.view", "reports.generate"},
    "center_director": {"centers.create", "centers.view", "students.create", "students.view", "ratings.view", "reports.generate"},
    "center_admin": {"centers.view", "students.create", "students.view", "ratings.view"},
    "teacher": {"students.view", "ratings.view"},
    "auditor": {"centers.view", "students.view", "ratings.view", "reports.generate", "audit_logs.view", "pinfl.reveal"},
    "parent": {"students.view", "ratings.view"},
    "external_api_consumer": {"aggregate_stats.read", "ratings.view"},
}

DEMO_USERS = [
    ("super_admin", "admin.tamor", "admin.tamor@tamor.local", None, "Tamor#2026Admin!", True),
    ("hokimiyat_operator", "operator.hokimiyat", "operator@tamor.local", None, "Hokim#Op2026!", True),
    ("center_director", "director.aspect", "director@aspect.local", None, "Direktor#2026!", True),
    ("center_admin", "admin.aspect", "admin@aspect.local", None, "CenterAdmin#26!", False),
    ("teacher", "teacher.dilnoza", "teacher@aspect.local", None, "Teach#Dil2026!", False),
    ("auditor", "auditor.tuman", "auditor@tamor.local", None, "Audit#Check26!", False),
]

PARENT_PHONE = "+998901234567"


def banner() -> None:
    print("=" * 72)
    print("WARNING: seeding demo identities for NON-PRODUCTION USE ONLY")
    print("Every created record is tagged with is_demo_account = true")
    print("=" * 72)


def guard_environment() -> None:
    if settings.is_production or os.getenv("ENVIRONMENT", "").lower() == "production":
        raise RuntimeError("seed_demo_users.py refuses to run in production.")


def get_or_create_role(session: Session, code: str, name_uz: str, name_ru: str, name_en: str) -> Role:
    role = session.execute(select(Role).where(Role.code == code)).scalar_one_or_none()
    if role is None:
        role = Role(code=code, name_uz=name_uz, name_ru=name_ru, name_en=name_en)
        session.add(role)
        session.flush()
    return role


def get_or_create_permission(session: Session, code: str, module: str, action: str) -> Permission:
    permission = session.execute(select(Permission).where(Permission.code == code)).scalar_one_or_none()
    if permission is None:
        permission = Permission(code=code, module=module, action=action)
        session.add(permission)
        session.flush()
    return permission


def ensure_center(session: Session) -> TrainingCenter:
    center = session.execute(select(TrainingCenter).where(TrainingCenter.tax_id == "309876543")).scalar_one_or_none()
    if center is None:
        center = TrainingCenter(
            name="Aspect Education Center",
            tax_id="309876543",
            director_full_name="Sardor Rakhmatov",
            phone="+998900001122",
            email="info@aspect.local",
            address="Toyloq district, central avenue 12",
            license_number="LIC-ASP-2026-001",
            center_type="private",
            is_active=True,
        )
        session.add(center)
        session.flush()
    return center


def ensure_role_permissions(session: Session) -> None:
    permission_map = {
        permission.code: permission
        for permission in session.execute(select(Permission)).scalars().all()
    }
    for role in session.execute(select(Role)).scalars().all():
        wanted = ROLE_PERMISSION_MAP.get(role.code, set())
        existing = {
            row.permission_id
            for row in session.execute(select(RolePermission).where(RolePermission.role_id == role.id)).scalars().all()
        }
        for permission_code in wanted:
            permission = permission_map[permission_code]
            if permission.id not in existing:
                session.add(RolePermission(role_id=role.id, permission_id=permission.id))


def upsert_user(
    session: Session,
    *,
    role: Role,
    username: str | None,
    email: str | None,
    phone: str | None,
    password: str | None,
    center_id,
    locale: str = "uz",
    enable_totp: bool = False,
) -> tuple[User, str | None]:
    query = select(User)
    if username:
        query = query.where(User.username == username)
    elif phone:
        query = query.where(User.phone == phone)
    else:
        raise ValueError("username or phone required")

    user = session.execute(query).scalar_one_or_none()
    secret_uri = None
    if user is None:
        user = User(
            username=username,
            email=email,
            phone=phone,
            role_id=role.id,
            center_id=center_id,
            locale_preference=locale,
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
            mfa_enabled=enable_totp,
            mfa_method=MFAMethod.totp if enable_totp else MFAMethod.none,
            password_changed_at=datetime.now(timezone.utc),
            must_change_password=False,
            is_demo_account=True,
        )
        session.add(user)
        session.flush()
    else:
        user.email = email
        user.phone = phone
        user.role_id = role.id
        user.center_id = center_id
        user.locale_preference = locale
        user.is_demo_account = True
        user.is_active = True
        user.mfa_enabled = enable_totp
        user.mfa_method = MFAMethod.totp if enable_totp else MFAMethod.none

    if password:
        user.password_hash = hash_password(password)
        user.password_changed_at = datetime.now(timezone.utc)
        session.execute(delete(PasswordHistory).where(PasswordHistory.user_id == user.id))
        session.add(
            PasswordHistory(
                user_id=user.id,
                password_hash=user.password_hash,
                created_at=datetime.now(timezone.utc),
            )
        )

    if enable_totp:
        secret = create_totp_secret()
        user.mfa_secret_encrypted = encrypt_totp_secret(secret)
        secret_uri = provisioning_uri(secret, username or phone or str(user.id))
        session.execute(delete(MFARecoveryCode).where(MFARecoveryCode.user_id == user.id))
        _, hashed_codes = generate_recovery_codes()
        for hashed in hashed_codes:
            session.add(
                MFARecoveryCode(
                    user_id=user.id,
                    code_hash=hashed,
                    used_at=None,
                    created_at=datetime.now(timezone.utc),
                )
            )
    else:
        user.mfa_secret_encrypted = None

    return user, secret_uri


def seed_api_consumer(session: Session, owner_user: User) -> tuple[str, str]:
    raw_key = f"tamor_demo_sk_live_{secrets.token_hex(8)}"
    raw_secret = secrets.token_urlsafe(32)
    api_key = session.execute(select(APIKey).where(APIKey.label == "Regional statistics demo")).scalar_one_or_none()
    if api_key is None:
        api_key = APIKey(
            label="Regional statistics demo",
            key_id=raw_key,
            key_hash=hash_secret(raw_key),
            secret_hash=hash_secret(raw_secret),
            secret_encrypted=encrypt_value(raw_secret),
            key_version=1,
            owner_user_id=owner_user.id,
            active_from=datetime.now(timezone.utc),
            grace_until=None,
            is_active=True,
            metadata_json={"is_demo_account": True},
        )
        session.add(api_key)
        session.flush()
        session.add(APIKeyScope(api_key_id=api_key.id, scope_code="aggregate_stats.read"))
    else:
        api_key.key_id = raw_key
        api_key.key_hash = hash_secret(raw_key)
        api_key.secret_hash = hash_secret(raw_secret)
        api_key.secret_encrypted = encrypt_value(raw_secret)
        api_key.owner_user_id = owner_user.id
    return raw_key, raw_secret


def main() -> None:
    guard_environment()
    banner()
    engine = create_engine(settings.sync_database_url)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        for role_args in ROLE_DEFINITIONS:
            get_or_create_role(session, *role_args)

        for permission_args in PERMISSIONS:
            get_or_create_permission(session, *permission_args)

        ensure_role_permissions(session)
        center = ensure_center(session)

        role_lookup = {role.code: role for role in session.execute(select(Role)).scalars().all()}
        seeded_uris: dict[str, str] = {}

        for role_code, username, email, phone, password, enable_totp in DEMO_USERS:
            _, uri = upsert_user(
                session,
                role=role_lookup[role_code],
                username=username,
                email=email,
                phone=phone,
                password=password,
                center_id=center.id if role_code in {"center_director", "center_admin", "teacher"} else None,
                enable_totp=enable_totp,
            )
            if uri:
                seeded_uris[username] = uri

        parent_user, _ = upsert_user(
            session,
            role=role_lookup["parent"],
            username=None,
            email=None,
            phone=PARENT_PHONE,
            password=None,
            center_id=None,
            enable_totp=False,
        )
        external_user, _ = upsert_user(
            session,
            role=role_lookup["external_api_consumer"],
            username="external.api",
            email="external@tamor.local",
            phone=None,
            password=secrets.token_urlsafe(18),
            center_id=None,
            enable_totp=False,
        )

        raw_key, raw_secret = seed_api_consumer(session, external_user)
        session.commit()

    print("\nDemo credentials:")
    for role_code, username, _, _, password, enable_totp in DEMO_USERS:
        print(f"- {role_code}: username={username} password={password} mfa={'totp' if enable_totp else 'disabled'}")
    print(f"- parent: phone={PARENT_PHONE} otp=printed by /api/v1/auth/parent/request-otp in development")
    print(f"- external_api_consumer: api_key={raw_key} hmac_secret={raw_secret}")

    if seeded_uris:
        print("\nSeeded TOTP provisioning URIs:")
        for username, uri in seeded_uris.items():
            print(f"* {username}: {uri}")
            qr = qrcode.QRCode(border=1)
            qr.add_data(uri)
            qr.print_ascii(invert=True)

    print(f"\nParent demo account id: {parent_user.id}")


if __name__ == "__main__":
    main()
