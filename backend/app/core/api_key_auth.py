"""API key authentication for external integrations."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.identity import ApiKey
from app.services import api_key_service


async def get_api_key_context(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-Api-Key"),
    db: AsyncSession = Depends(get_db),
) -> ApiKey:
    if not x_api_key:
        raise HTTPException(status_code=401, detail={"code": "API_KEY_REQUIRED"})

    api_key = await api_key_service.find_active_api_key(db, x_api_key)
    if not api_key:
        raise HTTPException(status_code=401, detail={"code": "INVALID_API_KEY"})

    request.state.api_key = api_key
    return api_key


def require_api_scope(scope: str):
    async def checker(
        api_key: ApiKey = Depends(get_api_key_context),
        db: AsyncSession = Depends(get_db),
    ) -> ApiKey:
        scopes = await api_key_service.get_api_key_scopes(db, api_key.id)
        if scope not in scopes:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
        return api_key

    return checker
