from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decrypt_value, hash_secret, verify_hmac_signature
from app.models import APIKey, APIKeyScope
from app.schemas.common import error_response, success_response


router = APIRouter(prefix="/public", tags=["public"])


async def require_hmac_api_key(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_api_key: str | None = Header(default=None),
    x_signature: str | None = Header(default=None),
    x_timestamp: str | None = Header(default=None),
) -> APIKey:
    if not x_api_key or not x_signature or not x_timestamp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("API_KEY_AUTH_REQUIRED")["error"],
        )

    try:
        request_time = datetime.fromisoformat(x_timestamp)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response("API_TIMESTAMP_INVALID")["error"],
        ) from exc

    if abs((datetime.now(timezone.utc) - request_time).total_seconds()) > 300:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("API_TIMESTAMP_EXPIRED")["error"],
        )

    result = await db.execute(select(APIKey).where(and_(APIKey.key_id == x_api_key, APIKey.is_active.is_(True))))
    api_key = result.scalar_one_or_none()
    if api_key is None or api_key.key_hash != hash_secret(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("API_KEY_INVALID")["error"],
        )

    body = await request.body()
    secret = decrypt_value(api_key.secret_encrypted)
    if not verify_hmac_signature(secret, request.method, request.url.path, x_timestamp, body, x_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("API_SIGNATURE_INVALID")["error"],
        )

    if api_key.grace_until and api_key.grace_until < datetime.now(timezone.utc) - timedelta(hours=24):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("API_KEY_EXPIRED")["error"],
        )

    scope_result = await db.execute(
        select(APIKeyScope).where(
            and_(APIKeyScope.api_key_id == api_key.id, APIKeyScope.scope_code == "aggregate_stats.read")
        )
    )
    if scope_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("API_SCOPE_DENIED")["error"],
        )

    api_key.last_used_at = datetime.now(timezone.utc)
    return api_key


@router.get("/aggregate-stats")
async def aggregate_stats(
    _: APIKey = Depends(require_hmac_api_key),
):
    return success_response(
        {
            "centers": 0,
            "students": 0,
            "teachers": 0,
            "certificates": 0,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
