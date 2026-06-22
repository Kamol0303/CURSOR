import secrets
import time
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pyotp
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.permissions import MANDATORY_MFA_ROLES, ROLE_PERMISSIONS
from app.core.redis_client import check_rate_limit
from app.core.security import (
    constant_time_elapsed,
    create_access_token,
    decrypt_totp_secret,
    device_fingerprint_hash,
    DUMMY_PASSWORD_HASH,
    encrypt_totp_secret,
    generate_refresh_token,
    hash_token,
    verify_password,
)
from app.models.identity import (
    DeviceFingerprint,
    LoginAuditLog,
    RefreshToken,
    SecurityEvent,
    User,
)


class AuthError(Exception):
    def __init__(self, code: str, status: int = 401):
        self.code = code
        self.status = status
        super().__init__(code)


MFA_ISSUER = "TaMoR"
MFA_SETUP_TTL_SECONDS = 600


async def _log_login(
    db: AsyncSession,
    *,
    username: str | None,
    user_id: UUID | None,
    ip: str | None,
    user_agent: str | None,
    success: bool,
    failure_reason: str | None = None,
    mfa_used: bool = False,
) -> None:
    db.add(
        LoginAuditLog(
            user_id=user_id,
            username_attempted=username,
            ip_address=ip,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            mfa_used=mfa_used,
        )
    )


async def _record_security_event(
    db: AsyncSession,
    *,
    event_type: str,
    severity: str,
    user_id: UUID | None = None,
    ip: str | None = None,
    details: dict | None = None,
) -> None:
    db.add(
        SecurityEvent(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip,
            details=details or {},
        )
    )


async def login_with_password(
    db: AsyncSession,
    *,
    username: str,
    password: str,
    ip: str | None,
    user_agent: str | None,
    client_hint: str = "",
) -> dict:
    start = time.perf_counter()
    try:
        ip_key = f"login:ip:{ip or 'unknown'}"
        if not await check_rate_limit(ip_key, 30, 300):
            raise AuthError("RATE_LIMIT_EXCEEDED", 429)

        account_key = f"login:account:{username.lower()}"
        if not await check_rate_limit(account_key, 10, 300):
            raise AuthError("RATE_LIMIT_EXCEEDED", 429)

        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.username == username, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()

        password_valid = False
        if user and user.password_hash:
            password_valid = verify_password(user.password_hash, password)
        else:
            verify_password(DUMMY_PASSWORD_HASH, password)

        if user is None or not password_valid:
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                    user.is_locked = True
                await _log_login(
                    db,
                    username=username,
                    user_id=user.id if user else None,
                    ip=ip,
                    user_agent=user_agent,
                    success=False,
                    failure_reason="INVALID_CREDENTIALS",
                )
            else:
                await _log_login(
                    db,
                    username=username,
                    user_id=None,
                    ip=ip,
                    user_agent=user_agent,
                    success=False,
                    failure_reason="INVALID_CREDENTIALS",
                )
            raise AuthError("INVALID_CREDENTIALS")

        if not user.is_active or user.is_locked:
            await _log_login(
                db,
                username=username,
                user_id=user.id,
                ip=ip,
                user_agent=user_agent,
                success=False,
                failure_reason="ACCOUNT_LOCKED",
            )
            raise AuthError("ACCOUNT_LOCKED", 403)

        if user.must_change_password:
            raise AuthError("PASSWORD_CHANGE_REQUIRED", 403)

        role_code = user.role.code
        requires_mfa = role_code in MANDATORY_MFA_ROLES or user.mfa_enabled

        if requires_mfa:
            if not user.mfa_secret_encrypted:
                setup_token = secrets.token_urlsafe(32)
                user.login_state = "pending_mfa_setup"
                user.login_state_expires_at = datetime.now(UTC) + timedelta(minutes=10)
                await db.flush()
                await cache_mfa_setup_token(setup_token, user.id)
                await _log_login(
                    db,
                    username=username,
                    user_id=user.id,
                    ip=ip,
                    user_agent=user_agent,
                    success=True,
                    failure_reason=None,
                )
                return {
                    "requires_mfa_setup": True,
                    "setup_token": setup_token,
                }

            mfa_token = secrets.token_urlsafe(32)
            user.login_state = "pending_mfa"
            user.login_state_expires_at = datetime.now(UTC) + timedelta(minutes=5)
            await db.flush()
            await cache_mfa_token(mfa_token, user.id)
            await _log_login(
                db,
                username=username,
                user_id=user.id,
                ip=ip,
                user_agent=user_agent,
                success=True,
                failure_reason=None,
            )
            return {
                "requires_mfa": True,
                "mfa_token": mfa_token,
            }

        return await _issue_tokens(
            db,
            user=user,
            ip=ip,
            user_agent=user_agent,
            client_hint=client_hint,
        )
    finally:
        constant_time_elapsed(start)


async def cache_mfa_token(token: str, user_id: UUID) -> None:
    from app.core.redis_client import get_redis

    r = await get_redis()
    await r.setex(f"mfa:pending:{token}", 300, str(user_id))


async def get_mfa_user_id(token: str) -> UUID | None:
    from app.core.redis_client import get_redis

    r = await get_redis()
    val = await r.get(f"mfa:pending:{token}")
    return UUID(val) if val else None


async def verify_mfa_and_issue_tokens(
    db: AsyncSession,
    *,
    mfa_token: str,
    code: str,
    ip: str | None,
    user_agent: str | None,
    client_hint: str = "",
) -> dict:
    user_id = await get_mfa_user_id(mfa_token)
    if not user_id:
        raise AuthError("MFA_SESSION_EXPIRED")

    rate_key = f"mfa:verify:{user_id}"
    if not await check_rate_limit(rate_key, settings.MFA_VERIFY_MAX_ATTEMPTS, settings.MFA_VERIFY_WINDOW_SECONDS):
        raise AuthError("MFA_RATE_LIMIT_EXCEEDED", 429)

    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user or user.login_state != "pending_mfa":
        raise AuthError("MFA_SESSION_EXPIRED")

    if not user.mfa_secret_encrypted:
        raise AuthError("MFA_NOT_CONFIGURED")

    secret = decrypt_totp_secret(user.mfa_secret_encrypted)
    totp = pyotp.TOTP(secret)
    if not totp.verify(code, valid_window=1):
        await _log_login(
            db,
            username=user.username,
            user_id=user.id,
            ip=ip,
            user_agent=user_agent,
            success=False,
            failure_reason="MFA_INVALID",
        )
        raise AuthError("MFA_INVALID")

    user.login_state = None
    user.login_state_expires_at = None
    user.failed_login_attempts = 0

    from app.core.redis_client import get_redis

    r = await get_redis()
    await r.delete(f"mfa:pending:{mfa_token}")

    tokens = await _issue_tokens(
        db,
        user=user,
        ip=ip,
        user_agent=user_agent,
        client_hint=client_hint,
        mfa_used=True,
    )
    return tokens


async def _issue_tokens(
    db: AsyncSession,
    *,
    user: User,
    ip: str | None,
    user_agent: str | None,
    client_hint: str = "",
    mfa_used: bool = False,
) -> dict:
    role_code = user.role.code
    permissions = ROLE_PERMISSIONS.get(role_code, [])
    access_token, jti, expires_at = create_access_token(
        user_id=user.id,
        role=role_code,
        center_id=user.center_id,
        permissions=permissions,
        locale=user.locale_preference,
    )

    refresh_token = generate_refresh_token()
    family_id = uuid4()
    refresh_expires = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            family_id=family_id,
            expires_at=refresh_expires,
        )
    )

    fp_hash = device_fingerprint_hash(user_agent or "", client_hint)
    existing = await db.execute(
        select(DeviceFingerprint).where(
            DeviceFingerprint.user_id == user.id,
            DeviceFingerprint.fingerprint_hash == fp_hash,
        )
    )
    device = existing.scalar_one_or_none()
    if device:
        device.last_seen_at = datetime.now(UTC)
    else:
        db.add(
            DeviceFingerprint(
                user_id=user.id,
                fingerprint_hash=fp_hash,
                trusted=False,
            )
        )

    user.last_login_at = datetime.now(UTC)
    user.failed_login_attempts = 0

    await _log_login(
        db,
        username=user.username,
        user_id=user.id,
        ip=ip,
        user_agent=user_agent,
        success=True,
        mfa_used=mfa_used,
    )

    return {
        "access_token": access_token,
        "expires_at": expires_at,
        "refresh_token": refresh_token,
        "requires_mfa": False,
    }


async def refresh_access_token(
    db: AsyncSession,
    *,
    refresh_token: str,
    ip: str | None,
    user_agent: str | None,
) -> dict:
    token_hash = hash_token(refresh_token)
    result = await db.execute(
        select(RefreshToken)
        .options(selectinload(RefreshToken.user).selectinload(User.role))
        .where(RefreshToken.token_hash == token_hash)
    )
    stored = result.scalar_one_or_none()

    if not stored or stored.revoked_at or stored.expires_at < datetime.now(UTC):
        raise AuthError("INVALID_REFRESH_TOKEN")

    if stored.used_at:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == stored.family_id)
            .values(revoked_at=datetime.now(UTC))
        )
        await _record_security_event(
            db,
            event_type="refresh_token_reuse",
            severity="critical",
            user_id=stored.user_id,
            ip=ip,
            details={"family_id": str(stored.family_id)},
        )
        raise AuthError("REFRESH_TOKEN_REUSE_DETECTED", 401)

    stored.used_at = datetime.now(UTC)
    user = stored.user
    if not user.is_active or user.is_locked:
        raise AuthError("ACCOUNT_LOCKED", 403)

    role_code = user.role.code
    permissions = ROLE_PERMISSIONS.get(role_code, [])
    access_token, jti, expires_at = create_access_token(
        user_id=user.id,
        role=role_code,
        center_id=user.center_id,
        permissions=permissions,
        locale=user.locale_preference,
    )

    new_refresh = generate_refresh_token()
    refresh_expires = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_refresh),
            family_id=stored.family_id,
            expires_at=refresh_expires,
        )
    )

    return {
        "access_token": access_token,
        "expires_at": expires_at,
        "refresh_token": new_refresh,
    }


async def logout(db: AsyncSession, *, refresh_token: str) -> None:
    token_hash = hash_token(refresh_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    stored = result.scalar_one_or_none()
    if stored:
        stored.revoked_at = datetime.now(UTC)


async def get_user_permissions(user: User) -> list[str]:
    return ROLE_PERMISSIONS.get(user.role.code, [])


async def cache_mfa_setup_token(token: str, user_id: UUID) -> None:
    from app.core.redis_client import get_redis

    r = await get_redis()
    await r.setex(f"mfa:setup:token:{token}", MFA_SETUP_TTL_SECONDS, str(user_id))


async def get_mfa_setup_user_id(token: str) -> UUID | None:
    from app.core.redis_client import get_redis

    r = await get_redis()
    val = await r.get(f"mfa:setup:token:{token}")
    return UUID(val) if val else None


async def cache_pending_mfa_secret(user_id: UUID, secret: str) -> None:
    from app.core.redis_client import get_redis

    r = await get_redis()
    await r.setex(f"mfa:setup:secret:{user_id}", MFA_SETUP_TTL_SECONDS, secret)


async def get_pending_mfa_secret(user_id: UUID) -> str | None:
    from app.core.redis_client import get_redis

    r = await get_redis()
    return await r.get(f"mfa:setup:secret:{user_id}")


async def _load_user_for_mfa_setup(db: AsyncSession, user_id: UUID) -> User:
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user or not user.is_active or user.is_locked:
        raise AuthError("ACCOUNT_INACTIVE", 403)
    return user


async def init_mfa_setup(
    db: AsyncSession,
    *,
    setup_token: str | None = None,
    user: User | None = None,
) -> dict:
    if setup_token:
        user_id = await get_mfa_setup_user_id(setup_token)
        if not user_id:
            raise AuthError("MFA_SETUP_EXPIRED")
        target = await _load_user_for_mfa_setup(db, user_id)
    elif user:
        target = user
        user_id = user.id
    else:
        raise AuthError("NOT_AUTHENTICATED", 401)

    if target.mfa_secret_encrypted and target.mfa_enabled:
        raise AuthError("MFA_ALREADY_ENABLED", 400)

    secret = pyotp.random_base32()
    await cache_pending_mfa_secret(user_id, secret)

    label = target.username or target.email or str(target.id)
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=label, issuer_name=MFA_ISSUER)

    return {
        "provisioning_uri": provisioning_uri,
        "secret": secret,
        "issuer": MFA_ISSUER,
        "setup_token": setup_token,
    }


async def confirm_mfa_setup(
    db: AsyncSession,
    *,
    code: str,
    setup_token: str | None = None,
    user: User | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    client_hint: str = "",
) -> dict:
    if setup_token:
        user_id = await get_mfa_setup_user_id(setup_token)
        if not user_id:
            raise AuthError("MFA_SETUP_EXPIRED")
        target = await _load_user_for_mfa_setup(db, user_id)
    elif user:
        target = user
        user_id = user.id
    else:
        raise AuthError("NOT_AUTHENTICATED", 401)

    pending_secret = await get_pending_mfa_secret(user_id)
    if not pending_secret:
        raise AuthError("MFA_SETUP_EXPIRED")

    totp = pyotp.TOTP(pending_secret)
    if not totp.verify(code, valid_window=1):
        raise AuthError("MFA_INVALID")

    was_first_login_setup = target.login_state == "pending_mfa_setup"
    target.mfa_secret_encrypted = encrypt_totp_secret(pending_secret)
    target.mfa_enabled = True
    target.login_state = None
    target.login_state_expires_at = None

    from app.core.redis_client import get_redis

    r = await get_redis()
    await r.delete(f"mfa:setup:secret:{user_id}")
    if setup_token:
        await r.delete(f"mfa:setup:token:{setup_token}")

    await _record_security_event(
        db,
        event_type="mfa_enabled",
        severity="info",
        user_id=target.id,
        ip=ip,
        details={"first_login_setup": was_first_login_setup},
    )

    if was_first_login_setup:
        return await _issue_tokens(
            db,
            user=target,
            ip=ip,
            user_agent=user_agent,
            client_hint=client_hint,
            mfa_used=True,
        )

    return {"mfa_enabled": True}


async def request_parent_otp(db: AsyncSession, *, phone: str, ip: str | None) -> dict:
    from app.core.rls import apply_rls_context, set_rls_role
    from app.integrations.sms_adapter import send_sms
    from app.models.education import Guardian

    set_rls_role("system")
    await apply_rls_context(db)

    ip_key = f"parent:otp:ip:{ip or 'unknown'}"
    if not await check_rate_limit(ip_key, 10, 300):
        raise AuthError("RATE_LIMIT_EXCEEDED", 429)

    phone_key = f"parent:otp:phone:{phone}"
    if not await check_rate_limit(phone_key, 5, 600):
        raise AuthError("RATE_LIMIT_EXCEEDED", 429)

    guardian = (
        await db.execute(select(Guardian).where(Guardian.phone == phone, Guardian.deleted_at.is_(None)))
    ).scalar_one_or_none()
    user = (
        await db.execute(
            select(User).options(selectinload(User.role)).where(User.phone == phone, User.deleted_at.is_(None))
        )
    ).scalar_one_or_none()

    if not guardian and (not user or user.role.code != "parent"):
        raise AuthError("PHONE_NOT_REGISTERED", 404)

    otp = f"{secrets.randbelow(900000) + 100000:06d}"
    from app.core.redis_client import cache_set

    await cache_set(
        f"parent:otp:{phone}",
        {"otp": otp, "attempts": 0},
        settings.PARENT_OTP_EXPIRE_SECONDS,
    )
    await send_sms(phone, f"TaMoR tasdiqlash kodi: {otp}")
    return {"sent": True, "expires_in": settings.PARENT_OTP_EXPIRE_SECONDS}


async def verify_parent_otp(
    db: AsyncSession,
    *,
    phone: str,
    otp: str,
    ip: str | None,
    user_agent: str | None,
    client_hint: str = "",
) -> dict:
    from app.core.redis_client import cache_get, get_redis
    from app.core.rls import apply_rls_context, set_rls_role
    from app.models.education import Guardian
    from app.models.identity import Role

    set_rls_role("system")
    await apply_rls_context(db)

    cached = await cache_get(f"parent:otp:{phone}")
    if not cached:
        raise AuthError("OTP_EXPIRED", 401)

    attempts = int(cached.get("attempts", 0)) + 1
    if attempts > settings.PARENT_OTP_MAX_ATTEMPTS:
        r = await get_redis()
        await r.delete(f"parent:otp:{phone}")
        raise AuthError("OTP_MAX_ATTEMPTS", 429)

    if cached.get("otp") != otp:
        from app.core.redis_client import cache_set

        await cache_set(
            f"parent:otp:{phone}",
            {"otp": cached["otp"], "attempts": attempts},
            settings.PARENT_OTP_EXPIRE_SECONDS,
        )
        raise AuthError("OTP_INVALID", 401)

    r = await get_redis()
    await r.delete(f"parent:otp:{phone}")

    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.phone == phone, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if not user:
        guardian = (
            await db.execute(select(Guardian).where(Guardian.phone == phone, Guardian.deleted_at.is_(None)))
        ).scalar_one_or_none()
        if not guardian:
            raise AuthError("PHONE_NOT_REGISTERED", 404)

        role_result = await db.execute(select(Role).where(Role.code == "parent"))
        parent_role = role_result.scalar_one()
        user = User(
            phone=phone,
            role_id=parent_role.id,
            is_active=True,
            locale_preference="uz",
            mfa_method="sms_otp",
        )
        db.add(user)
        await db.flush()
        await db.refresh(user, attribute_names=["role"])

    if user.role.code != "parent":
        raise AuthError("NOT_PARENT_ACCOUNT", 403)

    return await _issue_tokens(
        db,
        user=user,
        ip=ip,
        user_agent=user_agent,
        client_hint=client_hint,
        mfa_used=True,
    )
