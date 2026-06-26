"""MFA enrollment flow tests."""

import pyotp
import pytest

from app.core.redis_client import get_redis
from app.core.security import decrypt_totp_secret
from app.services.auth_service import (
    AuthError,
    _try_consume_backup_code,
    cache_mfa_setup_token,
    cache_pending_mfa_secret,
    confirm_mfa_setup,
    init_mfa_setup,
    login_with_password,
    regenerate_mfa_backup_codes,
)


@pytest.mark.integration
async def test_mandatory_role_first_login_requires_mfa_setup(db_session, security_fixtures):
    fx = security_fixtures
    director = fx["director_a"]
    director.mfa_secret_encrypted = None
    director.mfa_enabled = False
    await db_session.commit()

    r = await get_redis()
    await r.delete(f"login:account:{director.username.lower()}")

    result = await login_with_password(
        db_session,
        username=director.username,
        password="Test#DirectorA1!",
        ip="10.0.0.5",
        user_agent="pytest",
    )
    assert result["requires_mfa_setup"] is True
    assert result["setup_token"]


@pytest.mark.integration
async def test_mfa_setup_confirm_enables_and_issues_tokens(db_session, security_fixtures):
    fx = security_fixtures
    director = fx["director_a"]
    director.mfa_secret_encrypted = None
    director.mfa_enabled = False
    director.login_state = "pending_mfa_setup"
    await db_session.commit()

    setup_token = "test-setup-token-enrollment"
    await cache_mfa_setup_token(setup_token, director.id)

    secret = pyotp.random_base32()
    await cache_pending_mfa_secret(director.id, secret)
    code = pyotp.TOTP(secret).now()

    result = await confirm_mfa_setup(
        db_session,
        setup_token=setup_token,
        code=code,
        ip="10.0.0.6",
        user_agent="pytest",
    )
    await db_session.commit()

    assert "access_token" in result
    await db_session.refresh(director)
    assert director.mfa_enabled is True
    assert decrypt_totp_secret(director.mfa_secret_encrypted) == secret


@pytest.mark.integration
async def test_mfa_setup_rejects_invalid_code(db_session, security_fixtures):
    fx = security_fixtures
    teacher = fx["teacher_a"]
    setup_token = "test-setup-token-invalid"
    await cache_mfa_setup_token(setup_token, teacher.id)
    await cache_pending_mfa_secret(teacher.id, pyotp.random_base32())

    with pytest.raises(AuthError) as exc:
        await confirm_mfa_setup(
            db_session,
            setup_token=setup_token,
            code="000000",
            ip="10.0.0.7",
            user_agent="pytest",
        )
    assert exc.value.code == "MFA_INVALID"


@pytest.mark.integration
async def test_init_mfa_setup_for_authenticated_user(db_session, security_fixtures):
    fx = security_fixtures
    teacher = fx["teacher_a"]
    teacher.mfa_secret_encrypted = None
    teacher.mfa_enabled = False
    await db_session.commit()

    result = await init_mfa_setup(db_session, user=teacher)
    assert result["provisioning_uri"].startswith("otpauth://")
    assert len(result["secret"]) >= 16


@pytest.mark.integration
async def test_mfa_setup_generates_backup_codes(db_session, security_fixtures):
    fx = security_fixtures
    teacher = fx["teacher_a"]
    teacher.mfa_secret_encrypted = None
    teacher.mfa_enabled = False
    await db_session.commit()

    secret = pyotp.random_base32()
    await cache_pending_mfa_secret(teacher.id, secret)
    result = await confirm_mfa_setup(db_session, user=teacher, code=pyotp.TOTP(secret).now())
    await db_session.commit()

    assert result["mfa_enabled"] is True
    assert len(result["backup_codes"]) == 10


@pytest.mark.integration
async def test_backup_code_consumed_once(db_session, security_fixtures):
    fx = security_fixtures
    teacher = fx["teacher_a"]
    teacher.mfa_enabled = True
    await db_session.commit()

    codes = await regenerate_mfa_backup_codes(db_session, teacher)
    await db_session.commit()
    assert await _try_consume_backup_code(db_session, teacher.id, codes[0]) is True
    await db_session.commit()
    assert await _try_consume_backup_code(db_session, teacher.id, codes[0]) is False
