"""JWT JTI revocation tests."""

from uuid import uuid4

import pytest

from app.core.config import settings
from app.core.redis_client import deny_jti, is_jti_denied
from app.services.auth_service import logout, revoke_access_token_jti


@pytest.fixture(autouse=True)
def _memory_redis(monkeypatch):
    monkeypatch.setattr(settings, "USE_MEMORY_REDIS", True)
    monkeypatch.setattr(settings, "REDIS_URL", "memory://")


@pytest.mark.asyncio
async def test_deny_jti_blocks_subsequent_check():
    jti = f"test-jti-{uuid4()}"
    await deny_jti(jti, 120)
    assert await is_jti_denied(jti) is True


@pytest.mark.asyncio
async def test_revoke_access_token_jti_helper():
    jti = f"test-jti-{uuid4()}"
    await revoke_access_token_jti(jti, None)
    assert await is_jti_denied(jti) is True


@pytest.mark.integration
async def test_logout_denies_access_jti(db_session, security_fixtures):
    from app.core.security import verify_access_token
    from app.services.auth_service import _issue_tokens

    user = security_fixtures["teacher_a"]
    tokens = await _issue_tokens(
        db_session,
        user=user,
        ip="10.0.0.1",
        user_agent="pytest",
    )
    await db_session.commit()

    payload = verify_access_token(tokens["access_token"])
    jti = payload["jti"]

    await logout(
        db_session,
        refresh_token=tokens["refresh_token"],
        access_jti=jti,
        access_exp=payload.get("exp"),
    )
    await db_session.commit()

    assert await is_jti_denied(jti) is True
