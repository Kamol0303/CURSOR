"""Authentication security tests — rate limits, refresh rotation, parent OTP."""

import pytest
from sqlalchemy import select

from app.core.config import settings
from app.core.redis_client import get_redis
from app.models.education import Guardian
from app.services.auth_service import (
    AuthError,
    login_with_password,
    refresh_access_token,
    request_parent_otp,
    verify_parent_otp,
)
from app.services.auth_service import _issue_tokens


@pytest.mark.integration
async def test_login_rate_limit_per_account(db_session, security_fixtures):
    fx = security_fixtures
    username = fx["teacher_a"].username
    ip = "203.0.113.50"

    # Clear any prior rate limit keys for this test
    r = await get_redis()
    await r.delete(f"login:account:{username.lower()}")
    await r.delete(f"login:ip:{ip}")

    for i in range(10):
        with pytest.raises(AuthError) as exc:
            await login_with_password(
                db_session,
                username=username,
                password="wrong-password",
                ip=ip,
                user_agent="pytest",
            )
        assert exc.value.code == "INVALID_CREDENTIALS"

    with pytest.raises(AuthError) as exc:
        await login_with_password(
            db_session,
            username=username,
            password="wrong-password",
            ip=ip,
            user_agent="pytest",
        )
    assert exc.value.code == "RATE_LIMIT_EXCEEDED"


@pytest.mark.integration
async def test_refresh_token_reuse_revokes_family(db_session, security_fixtures):
    fx = security_fixtures
    user = fx["teacher_a"]

    tokens = await _issue_tokens(
        db_session,
        user=user,
        ip="10.0.0.1",
        user_agent="pytest",
    )
    await db_session.commit()

    old_refresh = tokens["refresh_token"]
    await refresh_access_token(
        db_session,
        refresh_token=old_refresh,
        ip="10.0.0.1",
        user_agent="pytest",
    )
    await db_session.commit()

    with pytest.raises(AuthError) as exc:
        await refresh_access_token(
            db_session,
            refresh_token=old_refresh,
            ip="10.0.0.1",
            user_agent="pytest",
        )
    assert exc.value.code == "REFRESH_TOKEN_REUSE_DETECTED"


@pytest.mark.integration
async def test_parent_otp_max_attempts(db_session, security_fixtures):
    fx = security_fixtures
    phone = fx["parent"].phone
    ip = "203.0.113.51"

    r = await get_redis()
    await r.delete(f"parent:otp:phone:{phone}")
    await r.delete(f"parent:otp:ip:{ip}")

    guardian = (
        await db_session.execute(select(Guardian).where(Guardian.phone == phone))
    ).scalar_one_or_none()
    assert guardian is not None

    await request_parent_otp(db_session, phone=phone, ip=ip)
    await db_session.commit()

    for _ in range(settings.PARENT_OTP_MAX_ATTEMPTS):
        with pytest.raises(AuthError) as exc:
            await verify_parent_otp(
                db_session,
                phone=phone,
                otp="000000",
                ip=ip,
                user_agent="pytest",
            )
        assert exc.value.code == "OTP_INVALID"

    with pytest.raises(AuthError) as exc:
        await verify_parent_otp(
            db_session,
            phone=phone,
            otp="000000",
            ip=ip,
            user_agent="pytest",
        )
    assert exc.value.code == "OTP_MAX_ATTEMPTS"
