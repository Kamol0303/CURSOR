from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import verify_access_token

bearer_scheme = HTTPBearer(auto_error=False)

ANALYTICS_PERMISSIONS = {"analytics.view", "system.settings"}


async def require_analytics_access(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail={"code": "NOT_AUTHENTICATED"})
    try:
        payload = verify_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN"}) from None

    permissions: list[str] = payload.get("permissions", [])
    if not any(p in permissions for p in ANALYTICS_PERMISSIONS):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    return payload
