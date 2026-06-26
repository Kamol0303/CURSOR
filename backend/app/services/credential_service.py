"""Centralized temporary credential issuance for staff onboarding."""

from __future__ import annotations

import secrets
import string
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.education import Teacher
from app.models.identity import User
from app.services.auth_service import AuthError, _record_security_event, revoke_all_user_refresh_tokens
from app.core.security import hash_password, validate_password_policy

_ISSUER_ROLES = frozenset({"super_admin", "center_director"})
_TARGET_ROLES_DIRECTOR = frozenset({"teacher", "center_admin", "student"})


def generate_temp_password(length: int = 14) -> str:
    """Generate a password that satisfies the default policy."""
    lowers = string.ascii_lowercase
    uppers = string.ascii_uppercase
    digits = string.digits
    specials = "!@#$%&*"
    parts = [
        secrets.choice(lowers),
        secrets.choice(uppers),
        secrets.choice(digits),
        secrets.choice(specials),
    ]
    pool = lowers + uppers + digits + specials
    parts.extend(secrets.choice(pool) for _ in range(max(length - len(parts), 0)))
    secrets.SystemRandom().shuffle(parts)
    password = "".join(parts)
    if validate_password_policy(password):
        return generate_temp_password(length)
    return password


async def _get_target_user(db: AsyncSession, target_user_id: UUID) -> User:
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == target_user_id, User.deleted_at.is_(None), User.is_active.is_(True))
    )
    target = result.scalar_one_or_none()
    if not target:
        raise AuthError("NOT_FOUND", 404)
    return target


def _assert_can_manage_target(issuer: User, target: User) -> None:
    if issuer.role.code not in _ISSUER_ROLES:
        raise AuthError("FORBIDDEN", 403)
    if issuer.role.code == "super_admin":
        return
    if target.center_id != issuer.center_id:
        raise AuthError("FORBIDDEN", 403)
    if target.role.code not in _TARGET_ROLES_DIRECTOR:
        raise AuthError("FORBIDDEN", 403)


async def apply_password(
    db: AsyncSession,
    target: User,
    new_password: str,
    *,
    must_change_password: bool = False,
) -> None:
    policy_errors = validate_password_policy(new_password)
    if policy_errors:
        raise AuthError(policy_errors[0], 422)
    target.password_hash = hash_password(new_password)
    target.password_changed_at = None if must_change_password else target.password_changed_at
    target.must_change_password = must_change_password
    target.failed_login_attempts = 0
    target.is_locked = False
    await db.flush()


async def issue_credentials(
    db: AsyncSession,
    issuer: User,
    *,
    target_user_id: UUID,
    ip: str | None = None,
) -> dict:
    target = await _get_target_user(db, target_user_id)
    _assert_can_manage_target(issuer, target)

    temp_password = generate_temp_password()
    await apply_password(db, target, temp_password, must_change_password=True)
    await revoke_all_user_refresh_tokens(db, target.id)

    login = target.username or target.phone or target.email or str(target.id)
    await _record_security_event(
        db,
        event_type="credential_issued",
        severity="info",
        user_id=issuer.id,
        ip=ip,
        details={
            "issuer_id": str(issuer.id),
            "target_user_id": str(target.id),
            "target_login": login,
            "target_role": target.role.code,
        },
    )

    return {
        "user_id": str(target.id),
        "login": login,
        "username": target.username,
        "role": target.role.code,
        "temporary_password": temp_password,
        "must_change_password": True,
    }


async def list_credential_targets(
    db: AsyncSession,
    issuer: User,
    *,
    search: str | None = None,
    limit: int = 30,
) -> list[dict]:
    if issuer.role.code not in _ISSUER_ROLES:
        raise AuthError("FORBIDDEN", 403)

    stmt = (
        select(User)
        .options(selectinload(User.role))
        .where(User.deleted_at.is_(None), User.is_active.is_(True), User.is_demo_account.is_(False))
        .order_by(User.username.nulls_last())
        .limit(limit)
    )
    if issuer.role.code == "center_director":
        stmt = stmt.where(
            User.center_id == issuer.center_id,
            User.role.has(code=list(_TARGET_ROLES_DIRECTOR)),
        )
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                User.username.ilike(pattern),
                User.phone.ilike(pattern),
                User.email.ilike(pattern),
            )
        )

    users = (await db.execute(stmt)).scalars().all()
    teacher_names: dict[UUID, str] = {}
    teacher_ids = [u.id for u in users if u.role.code == "teacher"]
    if teacher_ids:
        t_rows = await db.execute(
            select(Teacher.user_id, Teacher.full_name).where(
                Teacher.user_id.in_(teacher_ids), Teacher.deleted_at.is_(None)
            )
        )
        teacher_names = {row[0]: row[1] for row in t_rows.all() if row[0]}

    return [
        {
            "id": str(u.id),
            "username": u.username,
            "phone": u.phone,
            "role": u.role.code,
            "display_name": teacher_names.get(u.id) or u.username or u.phone or u.email or str(u.id),
        }
        for u in users
        if u.id != issuer.id
    ]
