from uuid import UUID

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.redis_client import is_jti_denied
from app.core.rls import apply_rls_context, set_rls_user
from app.core.security import verify_access_token
from app.models.identity import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail={"code": "NOT_AUTHENTICATED"})

    try:
        payload = verify_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN"}) from None

    jti = payload.get("jti")
    if jti and await is_jti_denied(jti):
        raise HTTPException(status_code=401, detail={"code": "TOKEN_REVOKED"})

    user_id = UUID(payload["sub"])
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user or not user.is_active or user.is_locked:
        raise HTTPException(status_code=401, detail={"code": "ACCOUNT_INACTIVE"})

    set_rls_user(user)
    await apply_rls_context(db)

    request.state.token_payload = payload
    return user


async def get_current_user_optional(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not credentials:
        return None

    try:
        payload = verify_access_token(credentials.credentials)
    except ValueError:
        return None

    jti = payload.get("jti")
    if jti and await is_jti_denied(jti):
        return None

    user_id = UUID(payload["sub"])
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user or not user.is_active or user.is_locked:
        return None

    set_rls_user(user)
    await apply_rls_context(db)

    request.state.token_payload = payload
    return user


def requires_permission(permission: str):
    async def checker(
        request: Request,
        user: User = Depends(get_current_user),
    ) -> User:
        payload = getattr(request.state, "token_payload", {})
        permissions: list[str] = payload.get("permissions", [])
        if permission not in permissions:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
        return user

    return checker
