from __future__ import annotations

import secrets
import uuid
from datetime import timedelta

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    generate_family_id,
    generate_opaque_token,
    hash_secret,
    now_utc,
    serialize_device_info,
    verify_password,
)
from app.models import (
    LoginAuditLog,
    MFARecoveryCode,
    MFAMethod,
    OTPChallenge,
    PasswordHistory,
    Permission,
    RefreshToken,
    RolePermission,
    Session,
    User,
)
from app.schemas.auth import LoginResult, UserSummary
from app.services.mfa import verify_totp_code
from app.services.password_policy import password_rotation_required


settings = get_settings()
serializer = URLSafeTimedSerializer(settings.mfa_encryption_key)
MANDATORY_MFA_ROLES = {"super_admin", "hokimiyat_operator", "center_director"}


class AuthError(Exception):
    def __init__(self, code: str, field: str | None = None):
        self.code = code
        self.field = field
        super().__init__(code)


async def _permissions_for_user(db: AsyncSession, user: User) -> list[str]:
    query = (
        select(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(RolePermission.role_id == user.role_id)
    )
    result = await db.execute(query)
    return list(result.scalars())


def _user_summary(user: User) -> UserSummary:
    return UserSummary(
        id=str(user.id),
        username=user.username,
        email=user.email,
        phone=user.phone,
        role=user.role.code,
        center_id=str(user.center_id) if user.center_id else None,
        locale_preference=user.locale_preference.value,
        mfa_enabled=user.mfa_enabled,
    )


async def _write_login_audit(
    db: AsyncSession,
    *,
    user: User | None,
    username_attempted: str,
    ip_address: str | None,
    user_agent: str | None,
    success: bool,
    failure_reason: str | None = None,
    mfa_used: bool = False,
) -> None:
    db.add(
        LoginAuditLog(
            user_id=user.id if user else None,
            username_attempted=username_attempted,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            mfa_used=mfa_used,
            created_at=now_utc(),
        )
    )
    await db.flush()


def _lockout_minutes(lockout_count: int) -> int:
    return 15 * (2 ** max(lockout_count - 1, 0))


async def _register_failed_password(
    db: AsyncSession,
    user: User,
    ip_address: str | None,
    user_agent: str | None,
) -> None:
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= 5:
        user.lockout_count += 1
        user.is_locked = True
        user.locked_until = now_utc() + timedelta(minutes=_lockout_minutes(user.lockout_count))
        user.failed_login_attempts = 0
    await _write_login_audit(
        db,
        user=user,
        username_attempted=user.username or user.phone or "",
        ip_address=ip_address,
        user_agent=user_agent,
        success=False,
        failure_reason="INVALID_CREDENTIALS",
    )


async def _ensure_password_auth_user(db: AsyncSession, username: str) -> User:
    query: Select[tuple[User]] = select(User).where(and_(User.username == username, User.deleted_at.is_(None)))
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user is None:
        await _write_login_audit(
            db,
            user=None,
            username_attempted=username,
            ip_address=None,
            user_agent=None,
            success=False,
            failure_reason="INVALID_CREDENTIALS",
        )
        raise AuthError("INVALID_CREDENTIALS", "username")
    return user


async def _issue_session_tokens(
    db: AsyncSession,
    user: User,
    *,
    ip_address: str | None,
    user_agent: str | None,
    family_id: str | None = None,
    session_id: uuid.UUID | None = None,
) -> tuple[LoginResult, str]:
    permissions = await _permissions_for_user(db, user)
    raw_refresh = generate_opaque_token()
    refresh_hash = hash_secret(raw_refresh)
    expires_at = now_utc() + timedelta(days=settings.refresh_token_days)

    if family_id is None:
        family_id = generate_family_id()
    if session_id is None:
        session = Session(
            user_id=user.id,
            refresh_token_hash=refresh_hash,
            device_info=serialize_device_info(user_agent),
            ip_address=ip_address,
            created_at=now_utc(),
            expires_at=expires_at,
            revoked_at=None,
        )
        db.add(session)
        await db.flush()
        session_id = session.id

    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=refresh_hash,
        family_id=family_id,
        session_id=session_id,
        expires_at=expires_at,
        used_at=None,
        revoked_at=None,
        replaced_by_token_hash=None,
    )
    db.add(refresh_token)
    user.last_login_at = now_utc()

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role.code,
        permissions=permissions,
        center_id=str(user.center_id) if user.center_id else None,
        locale=user.locale_preference.value,
    )
    result = LoginResult(
        access_token=access_token,
        expires_in=settings.access_token_minutes * 60,
        mfa_required=False,
        must_change_password=user.must_change_password
        or password_rotation_required(user.role.code, user.password_changed_at),
        user=_user_summary(user),
    )
    return result, raw_refresh


def _mfa_required(user: User) -> bool:
    role_code = user.role.code
    if role_code in MANDATORY_MFA_ROLES:
        return True
    return user.mfa_enabled and user.mfa_method != MFAMethod.none


async def authenticate_password_login(
    db: AsyncSession,
    *,
    username: str,
    password: str,
    ip_address: str | None,
    user_agent: str | None,
) -> tuple[LoginResult, str | None]:
    user = await _ensure_password_auth_user(db, username)

    if not user.is_active:
        raise AuthError("USER_INACTIVE")

    if user.locked_until and user.locked_until > now_utc():
        await _write_login_audit(
            db,
            user=user,
            username_attempted=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason="ACCOUNT_LOCKED",
        )
        raise AuthError("ACCOUNT_LOCKED")

    if not user.password_hash or not verify_password(password, user.password_hash):
        await _register_failed_password(db, user, ip_address, user_agent)
        raise AuthError("INVALID_CREDENTIALS", "password")

    user.failed_login_attempts = 0
    user.is_locked = False
    user.locked_until = None

    if _mfa_required(user):
        if not user.mfa_secret_encrypted and user.mfa_method == MFAMethod.totp:
            raise AuthError("MFA_NOT_CONFIGURED")
        challenge_token = serializer.dumps({"user_id": str(user.id), "nonce": secrets.token_urlsafe(8)})
        await _write_login_audit(
            db,
            user=user,
            username_attempted=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            failure_reason=None,
            mfa_used=False,
        )
        return (
            LoginResult(
                mfa_required=True,
                challenge_token=challenge_token,
                must_change_password=user.must_change_password
                or password_rotation_required(user.role.code, user.password_changed_at),
                user=_user_summary(user),
            ),
            None,
        )

    await _write_login_audit(
        db,
        user=user,
        username_attempted=username,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True,
        failure_reason=None,
        mfa_used=False,
    )
    return await _issue_session_tokens(db, user, ip_address=ip_address, user_agent=user_agent)


async def complete_mfa_login(
    db: AsyncSession,
    *,
    challenge_token: str,
    code: str,
    ip_address: str | None,
    user_agent: str | None,
) -> tuple[LoginResult, str]:
    try:
        payload = serializer.loads(challenge_token, max_age=300)
        user_id = uuid.UUID(payload["user_id"])
    except SignatureExpired as exc:
        raise AuthError("MFA_CHALLENGE_EXPIRED") from exc
    except BadSignature as exc:
        raise AuthError("MFA_CHALLENGE_INVALID") from exc

    user = await db.get(User, user_id)
    if user is None:
        raise AuthError("USER_NOT_FOUND")

    valid = False
    if user.mfa_method == MFAMethod.totp and user.mfa_secret_encrypted:
        valid = verify_totp_code(user.mfa_secret_encrypted, code)
    if not valid:
        recovery = await db.execute(
            select(MFARecoveryCode).where(
                and_(
                    MFARecoveryCode.user_id == user.id,
                    MFARecoveryCode.code_hash == hash_secret(code.upper()),
                    MFARecoveryCode.used_at.is_(None),
                )
            )
        )
        recovery_code = recovery.scalar_one_or_none()
        if recovery_code is not None:
            recovery_code.used_at = now_utc()
            valid = True

    if not valid:
        raise AuthError("MFA_CODE_INVALID", "code")

    await _write_login_audit(
        db,
        user=user,
        username_attempted=user.username or "",
        ip_address=ip_address,
        user_agent=user_agent,
        success=True,
        failure_reason=None,
        mfa_used=True,
    )
    return await _issue_session_tokens(db, user, ip_address=ip_address, user_agent=user_agent)


async def refresh_session(
    db: AsyncSession, *, raw_refresh_token: str, ip_address: str | None, user_agent: str | None
) -> tuple[LoginResult, str]:
    token_hash = hash_secret(raw_refresh_token)
    token_result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    token = token_result.scalar_one_or_none()
    if token is None:
        raise AuthError("REFRESH_TOKEN_INVALID")

    if token.revoked_at or token.used_at:
        await revoke_refresh_family(db, token.family_id)
        raise AuthError("REFRESH_TOKEN_REPLAY_DETECTED")
    if token.expires_at <= now_utc():
        token.revoked_at = now_utc()
        raise AuthError("REFRESH_TOKEN_EXPIRED")

    user = await db.get(User, token.user_id)
    if user is None or not user.is_active:
        raise AuthError("USER_INACTIVE")

    token.used_at = now_utc()
    result, new_raw_refresh = await _issue_session_tokens(
        db,
        user,
        ip_address=ip_address,
        user_agent=user_agent,
        family_id=token.family_id,
        session_id=token.session_id,
    )
    token.replaced_by_token_hash = hash_secret(new_raw_refresh)
    return result, new_raw_refresh


async def revoke_refresh_family(db: AsyncSession, family_id: str) -> None:
    rows = await db.execute(select(RefreshToken).where(RefreshToken.family_id == family_id))
    for token in rows.scalars():
        token.revoked_at = now_utc()


async def logout_session(db: AsyncSession, *, raw_refresh_token: str | None) -> None:
    if not raw_refresh_token:
        return
    token_hash = hash_secret(raw_refresh_token)
    rows = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    token = rows.scalar_one_or_none()
    if token is not None:
        token.revoked_at = now_utc()


async def request_parent_otp(db: AsyncSession, phone: str, code_hash: str) -> OTPChallenge:
    challenge = OTPChallenge(
        phone=phone,
        purpose="parent_login",
        code_hash=code_hash,
        expires_at=now_utc() + timedelta(seconds=settings.parent_otp_ttl_seconds),
        attempts=0,
        consumed_at=None,
        created_at=now_utc(),
    )
    db.add(challenge)
    await db.flush()
    return challenge


async def verify_parent_otp(
    db: AsyncSession, *, phone: str, code: str, ip_address: str | None, user_agent: str | None
) -> tuple[LoginResult, str]:
    challenge_result = await db.execute(
        select(OTPChallenge)
        .where(
            and_(
                OTPChallenge.phone == phone,
                OTPChallenge.purpose == "parent_login",
                OTPChallenge.consumed_at.is_(None),
            )
        )
        .order_by(OTPChallenge.created_at.desc())
    )
    challenge = challenge_result.scalars().first()
    if challenge is None or challenge.expires_at <= now_utc():
        raise AuthError("OTP_EXPIRED", "code")

    if challenge.code_hash != hash_secret(code):
        challenge.attempts += 1
        raise AuthError("OTP_INVALID", "code")

    user_result = await db.execute(select(User).where(and_(User.phone == phone, User.deleted_at.is_(None))))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise AuthError("USER_NOT_FOUND", "phone")

    challenge.consumed_at = now_utc()
    await _write_login_audit(
        db,
        user=user,
        username_attempted=phone,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True,
        failure_reason=None,
        mfa_used=True,
    )
    return await _issue_session_tokens(db, user, ip_address=ip_address, user_agent=user_agent)


async def recent_password_hashes(db: AsyncSession, user_id: uuid.UUID) -> list[str]:
    rows = await db.execute(
        select(PasswordHistory.password_hash)
        .where(PasswordHistory.user_id == user_id)
        .order_by(PasswordHistory.created_at.desc())
        .limit(5)
    )
    return list(rows.scalars())
