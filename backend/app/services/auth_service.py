import uuid
from datetime import timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.datetime_utils import ensure_utc_aware, utc_now
from app.core.security import (
    MFA_MANDATORY_ROLES,
    PASSWORD_HISTORY_COUNT,
    calculate_lockout_until,
    check_password_history,
    create_access_token,
    decrypt_totp_secret,
    encrypt_totp_secret,
    generate_backup_codes,
    generate_otp_code,
    generate_refresh_token,
    generate_totp_secret,
    get_totp_uri,
    hash_password,
    hash_token,
    is_account_locked,
    validate_password_policy,
    verify_password,
    verify_totp,
)
from app.models import (
    LoginAuditLog,
    MfaBackupCode,
    OtpCode,
    PasswordHistory,
    RefreshToken,
    Role,
    RolePermission,
    User,
)
from app.schemas.auth import UserResponse
from app.services.password_policy import password_rotation_required

# In-memory MFA pending tokens for login flow (use Redis in production)
_mfa_pending: dict[str, dict] = {}


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_user_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(
                selectinload(User.role).selectinload(Role.role_permissions).selectinload(RolePermission.permission)
            )
            .where(User.username == username, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def _get_user_by_phone(self, phone: str) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(
                selectinload(User.role).selectinload(Role.role_permissions).selectinload(RolePermission.permission)
            )
            .where(User.phone == phone, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def _log_login(
        self,
        user_id: uuid.UUID | None,
        username: str | None,
        ip: str | None,
        user_agent: str | None,
        success: bool,
        failure_reason: str | None = None,
        mfa_used: bool = False,
    ):
        log = LoginAuditLog(
            user_id=user_id,
            username_attempted=username,
            ip_address=ip,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            mfa_used=mfa_used,
        )
        self.db.add(log)

    def _user_response(self, user: User) -> UserResponse:
        permissions = [rp.permission.code for rp in user.role.role_permissions]
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            role=user.role.code,
            role_name_uz=user.role.name_uz,
            role_name_ru=user.role.name_ru,
            role_name_en=user.role.name_en,
            center_id=user.center_id,
            locale_preference=user.locale_preference,
            mfa_enabled=user.mfa_enabled,
            must_change_password=user.must_change_password,
            permissions=permissions,
        )

    async def login(
        self, username: str, password: str, ip: str | None, user_agent: str | None
    ) -> dict:
        user = await self._get_user_by_username(username)
        if not user:
            await self._log_login(None, username, ip, user_agent, False, "USER_NOT_FOUND")
            return {"error": "INVALID_CREDENTIALS"}

        if not user.is_active:
            await self._log_login(user.id, username, ip, user_agent, False, "ACCOUNT_INACTIVE")
            return {"error": "ACCOUNT_INACTIVE"}

        if is_account_locked(user):
            await self._log_login(user.id, username, ip, user_agent, False, "ACCOUNT_LOCKED")
            return {"error": "ACCOUNT_LOCKED"}

        if not user.password_hash or not verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.is_locked = True
                user.locked_until = calculate_lockout_until(user.failed_login_attempts)
            await self._log_login(user.id, username, ip, user_agent, False, "INVALID_PASSWORD")
            await self.db.flush()
            return {"error": "INVALID_CREDENTIALS"}

        user.failed_login_attempts = 0
        user.is_locked = False
        user.locked_until = None

        mfa_required = user.mfa_enabled or user.role.code in MFA_MANDATORY_ROLES

        if mfa_required and user.mfa_enabled:
            mfa_token = uuid.uuid4().hex
            _mfa_pending[mfa_token] = {
                "user_id": str(user.id),
                "expires": utc_now() + timedelta(minutes=5),
            }
            await self._log_login(user.id, username, ip, user_agent, True)
            return {
                "mfa_required": True,
                "mfa_token": mfa_token,
                "must_change_password": user.must_change_password,
            }

        if mfa_required and not user.mfa_enabled:
            return {"error": "MFA_SETUP_REQUIRED"}

        return await self._complete_login(user, ip, user_agent)

    async def verify_mfa(
        self, mfa_token: str, code: str, ip: str | None, user_agent: str | None
    ) -> dict:
        pending = _mfa_pending.get(mfa_token)
        if not pending or utc_now() > pending["expires"]:
            _mfa_pending.pop(mfa_token, None)
            return {"error": "MFA_TOKEN_EXPIRED"}

        result = await self.db.execute(
            select(User)
            .options(
                selectinload(User.role).selectinload(Role.role_permissions).selectinload(RolePermission.permission)
            )
            .where(User.id == pending["user_id"])
        )
        user = result.scalar_one_or_none()
        if not user:
            return {"error": "USER_NOT_FOUND"}

        if user.mfa_secret_encrypted:
            secret = decrypt_totp_secret(user.mfa_secret_encrypted)
            if verify_totp(secret, code):
                _mfa_pending.pop(mfa_token, None)
                return await self._complete_login(user, ip, user_agent, mfa_used=True)

        backup_result = await self.db.execute(
            select(MfaBackupCode).where(
                MfaBackupCode.user_id == user.id, MfaBackupCode.used_at.is_(None)
            )
        )
        for backup in backup_result.scalars():
            if verify_password(code, backup.code_hash):
                backup.used_at = utc_now()
                _mfa_pending.pop(mfa_token, None)
                return await self._complete_login(user, ip, user_agent, mfa_used=True)

        return {"error": "MFA_INVALID_CODE"}

    async def _complete_login(
        self, user: User, ip: str | None, user_agent: str | None, mfa_used: bool = False
    ) -> dict:
        if user.must_change_password or password_rotation_required(
            user.role.code, user.password_changed_at
        ):
            user.must_change_password = True

        permissions = [rp.permission.code for rp in user.role.role_permissions]
        access_token = create_access_token(
            str(user.id),
            user.role.code,
            str(user.center_id) if user.center_id else None,
            permissions,
            user.locale_preference,
        )
        refresh_token = generate_refresh_token()
        family_id = uuid.uuid4()
        expires_at = utc_now() + timedelta(days=settings.jwt_refresh_token_expire_days)

        rt = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            family_id=family_id,
            expires_at=expires_at,
        )
        self.db.add(rt)

        user.last_login_at = utc_now()
        await self._log_login(user.id, user.username, ip, user_agent, True, mfa_used=mfa_used)
        await self.db.flush()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": self._user_response(user),
            "must_change_password": user.must_change_password,
        }

    async def refresh_tokens(self, refresh_token: str) -> dict:
        token_hash = hash_token(refresh_token)
        result = await self.db.execute(
            select(RefreshToken)
            .options(
                selectinload(RefreshToken.user)
                .selectinload(User.role)
                .selectinload(Role.role_permissions)
                .selectinload(RolePermission.permission)
            )
            .where(RefreshToken.token_hash == token_hash)
        )
        stored = result.scalar_one_or_none()

        if not stored:
            return {"error": "REFRESH_TOKEN_INVALID"}

        if stored.revoked_at or stored.used_at:
            await self.db.execute(
                update(RefreshToken)
                .where(RefreshToken.family_id == stored.family_id)
                .values(revoked_at=utc_now())
            )
            return {"error": "REFRESH_TOKEN_REPLAY_DETECTED"}

        if utc_now() > ensure_utc_aware(stored.expires_at):
            return {"error": "REFRESH_TOKEN_EXPIRED"}

        stored.used_at = utc_now()
        user = stored.user

        permissions = [rp.permission.code for rp in user.role.role_permissions]
        new_access = create_access_token(
            str(user.id),
            user.role.code,
            str(user.center_id) if user.center_id else None,
            permissions,
            user.locale_preference,
        )
        new_refresh = generate_refresh_token()
        new_rt = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_refresh),
            family_id=stored.family_id,
            expires_at=utc_now() + timedelta(days=settings.jwt_refresh_token_expire_days),
        )
        self.db.add(new_rt)
        await self.db.flush()

        return {"access_token": new_access, "refresh_token": new_refresh}

    async def logout(self, refresh_token: str) -> None:
        token_hash = hash_token(refresh_token)
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(revoked_at=utc_now())
        )

    async def request_otp(self, phone: str) -> dict:
        user = await self._get_user_by_phone(phone)
        if not user or user.role.code != "parent":
            return {"error": "PHONE_NOT_REGISTERED"}

        code = generate_otp_code()
        otp = OtpCode(
            phone=phone,
            code_hash=hash_password(code),
            expires_at=utc_now() + timedelta(minutes=5),
        )
        self.db.add(otp)
        await self.db.flush()
        return {"otp_sent": True, "dev_code": code}

    async def verify_otp(
        self, phone: str, code: str, ip: str | None, user_agent: str | None
    ) -> dict:
        result = await self.db.execute(
            select(OtpCode)
            .where(OtpCode.phone == phone, OtpCode.used_at.is_(None))
            .order_by(OtpCode.created_at.desc())
            .limit(1)
        )
        otp = result.scalar_one_or_none()
        if not otp or utc_now() > ensure_utc_aware(otp.expires_at):
            return {"error": "OTP_EXPIRED"}

        if not verify_password(code, otp.code_hash):
            return {"error": "OTP_INVALID"}

        otp.used_at = utc_now()
        user = await self._get_user_by_phone(phone)
        if not user:
            return {"error": "USER_NOT_FOUND"}

        return await self._complete_login(user, ip, user_agent)

    async def setup_mfa(self, user: User) -> dict:
        secret = generate_totp_secret()
        user.mfa_secret_encrypted = encrypt_totp_secret(secret)
        user.mfa_enabled = True
        user.mfa_method = "totp"

        codes = generate_backup_codes()
        for code in codes:
            self.db.add(MfaBackupCode(user_id=user.id, code_hash=hash_password(code)))

        await self.db.flush()
        return {
            "secret": secret,
            "provisioning_uri": get_totp_uri(secret, user.username or str(user.id)),
            "backup_codes": codes,
        }

    async def change_password(self, user: User, current: str, new: str) -> dict:
        if not user.password_hash or not verify_password(current, user.password_hash):
            return {"error": "CURRENT_PASSWORD_INVALID"}

        valid, error_code = validate_password_policy(new)
        if not valid:
            return {"error": error_code}

        history_result = await self.db.execute(
            select(PasswordHistory.password_hash)
            .where(PasswordHistory.user_id == user.id)
            .order_by(PasswordHistory.created_at.desc())
            .limit(PASSWORD_HISTORY_COUNT)
        )
        if check_password_history(new, list(history_result.scalars())):
            return {"error": "PASSWORD_REUSED"}

        if user.password_hash:
            self.db.add(PasswordHistory(user_id=user.id, password_hash=user.password_hash))

        user.password_hash = hash_password(new)
        user.password_changed_at = utc_now()
        user.must_change_password = False
        await self.db.flush()
        return {"success": True}
