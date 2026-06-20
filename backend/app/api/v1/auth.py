from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_user_permissions
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import now_utc
from app.core.security import hash_secret
from app.models import MFARecoveryCode, MFAMethod, User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    MFAChallengeRequest,
    MeResponse,
    ParentOTPRequest,
    ParentOTPVerifyRequest,
)
from app.schemas.common import error_response, success_response
from app.services.auth import (
    AuthError,
    authenticate_password_login,
    complete_mfa_login,
    logout_session,
    refresh_session,
    request_parent_otp,
    verify_parent_otp,
)
from app.services.mfa import create_totp_secret, encrypt_totp_secret, generate_recovery_codes, provisioning_uri
from app.services.otp import dev_delivery_message, generate_sms_otp


router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _cookie_kwargs() -> dict[str, object]:
    return {
        "httponly": True,
        "secure": settings.is_production,
        "samesite": "strict",
        "path": "/",
        "max_age": settings.refresh_token_days * 24 * 60 * 60,
    }


def _auth_error_to_http(error: AuthError) -> HTTPException:
    status_code = status.HTTP_401_UNAUTHORIZED
    if error.code in {"OTP_INVALID", "OTP_EXPIRED", "MFA_CODE_INVALID"}:
        status_code = status.HTTP_400_BAD_REQUEST
    if error.code == "ACCOUNT_LOCKED":
        status_code = status.HTTP_423_LOCKED
    return HTTPException(status_code=status_code, detail=error_response(error.code, error.field)["error"])


@router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    try:
        result, refresh_token = await authenticate_password_login(
            db,
            username=payload.username,
            password=payload.password,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        await db.commit()
    except AuthError as exc:
        await db.commit()
        raise _auth_error_to_http(exc) from exc

    if refresh_token:
        response.set_cookie(settings.refresh_cookie_name, refresh_token, **_cookie_kwargs())
    return success_response(result.model_dump())


@router.post("/mfa/verify")
async def verify_mfa(
    payload: MFAChallengeRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    try:
        result, refresh_token = await complete_mfa_login(
            db,
            challenge_token=payload.challenge_token,
            code=payload.code,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        await db.commit()
    except AuthError as exc:
        await db.commit()
        raise _auth_error_to_http(exc) from exc

    response.set_cookie(settings.refresh_cookie_name, refresh_token, **_cookie_kwargs())
    return success_response(result.model_dump())


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("REFRESH_TOKEN_MISSING")["error"],
        )
    try:
        result, new_refresh = await refresh_session(
            db,
            raw_refresh_token=refresh_token,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        await db.commit()
    except AuthError as exc:
        await db.commit()
        raise _auth_error_to_http(exc) from exc

    response.set_cookie(settings.refresh_cookie_name, new_refresh, **_cookie_kwargs())
    return success_response(result.model_dump())


@router.post("/logout")
async def logout(
    payload: LogoutRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    refresh_token = payload.refresh_token or request.cookies.get(settings.refresh_cookie_name)
    await logout_session(db, raw_refresh_token=refresh_token)
    await db.commit()
    response.delete_cookie(settings.refresh_cookie_name, path="/")
    return success_response({"logged_out": True})


@router.post("/parent/request-otp")
async def parent_request_otp(payload: ParentOTPRequest, db: AsyncSession = Depends(get_db)):
    otp_code = generate_sms_otp()
    await request_parent_otp(db, phone=payload.phone, code_hash=hash_secret(otp_code))
    await db.commit()
    return success_response(
        {
            "message": "OTP_SENT",
            "delivery": dev_delivery_message(payload.phone, otp_code) if not settings.is_production else None,
        }
    )


@router.post("/parent/verify-otp")
async def parent_verify_otp(
    payload: ParentOTPVerifyRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    try:
        result, refresh_token = await verify_parent_otp(
            db,
            phone=payload.phone,
            code=payload.code,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        await db.commit()
    except AuthError as exc:
        await db.commit()
        raise _auth_error_to_http(exc) from exc

    response.set_cookie(settings.refresh_cookie_name, refresh_token, **_cookie_kwargs())
    return success_response(result.model_dump())


@router.get("/me")
async def me(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    permissions = await get_user_permissions(db, user)
    payload = MeResponse(
        user={
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "role": user.role.code,
            "center_id": str(user.center_id) if user.center_id else None,
            "locale_preference": user.locale_preference.value,
            "mfa_enabled": user.mfa_enabled,
        },
        permissions=permissions,
    )
    return success_response(payload.model_dump())


@router.post("/mfa/setup")
async def setup_mfa(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    secret = create_totp_secret()
    user.mfa_secret_encrypted = encrypt_totp_secret(secret)
    user.mfa_enabled = True
    user.mfa_method = MFAMethod.totp
    raw_codes, hashed_codes = generate_recovery_codes()
    for hashed in hashed_codes:
        db.add(MFARecoveryCode(user_id=user.id, code_hash=hashed, used_at=None, created_at=now_utc()))
    await db.commit()
    return success_response(
        {
            "provisioning_uri": provisioning_uri(secret, user.username or user.phone or str(user.id)),
            "recovery_codes": raw_codes,
        }
    )
