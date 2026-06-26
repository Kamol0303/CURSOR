<<<<<<< HEAD
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
=======
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import bearer_scheme, get_current_user, get_current_user_optional, requires_permission
from app.models.identity import User
from app.schemas.auth import (
    ApiResponse,
    LoginRequest,
    MfaSetupConfirmRequest,
    MfaSetupInitRequest,
    MfaVerifyRequest,
    ParentOtpRequest,
    ParentOtpVerifyRequest,
    ChangePasswordRequest,
    AdminResetPasswordRequest,
    TokenResponse,
    UserMeResponse,
)
from app.services.auth_service import (
    AuthError,
    confirm_mfa_setup,
    get_user_permissions,
    init_mfa_setup,
    login_with_password,
    logout,
    change_password,
    admin_reset_password,
    refresh_access_token,
    request_parent_otp,
    verify_mfa_and_issue_tokens,
    verify_parent_otp,
)
from app.core.permissions import MANDATORY_MFA_ROLES
from app.core.security import verify_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "tmb_refresh"


def _set_refresh_cookie(response: Response, token: str) -> None:
    from app.core.config import settings

    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=settings.ENVIRONMENT not in ("development", "test"),
        samesite="strict",
        max_age=7 * 24 * 3600,
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE, path="/api/v1/auth")


@router.post("/login", response_model=ApiResponse)
async def login(
    body: LoginRequest,
>>>>>>> main
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    try:
<<<<<<< HEAD
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
=======
        result = await login_with_password(
            db,
            username=body.username,
            password=body.password,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            client_hint=request.headers.get("x-client-hint", ""),
        )
    except AuthError as exc:
        raise HTTPException(status_code=exc.status, detail={"code": exc.code}) from exc

    if result.get("requires_mfa_setup"):
        return ApiResponse(
            success=True,
            data={
                "requires_mfa_setup": True,
                "setup_token": result["setup_token"],
            },
        )

    if result.get("requires_mfa"):
        return ApiResponse(
            success=True,
            data={
                "requires_mfa": True,
                "mfa_token": result["mfa_token"],
            },
        )

    _set_refresh_cookie(response, result["refresh_token"])
    return ApiResponse(
        success=True,
        data=TokenResponse(
            access_token=result["access_token"],
            expires_at=result["expires_at"],
        ).model_dump(),
    )


@router.post("/mfa/verify", response_model=ApiResponse)
async def mfa_verify(
    body: MfaVerifyRequest,
>>>>>>> main
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    try:
<<<<<<< HEAD
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
=======
        result = await verify_mfa_and_issue_tokens(
            db,
            mfa_token=body.mfa_token,
            code=body.code,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            client_hint=request.headers.get("x-client-hint", ""),
        )
    except AuthError as exc:
        raise HTTPException(status_code=exc.status, detail={"code": exc.code}) from exc

    _set_refresh_cookie(response, result["refresh_token"])
    return ApiResponse(
        success=True,
        data=TokenResponse(
            access_token=result["access_token"],
            expires_at=result["expires_at"],
        ).model_dump(),
    )


@router.post("/mfa/setup/init", response_model=ApiResponse)
async def mfa_setup_init(
    body: MfaSetupInitRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    try:
        if body.setup_token:
            result = await init_mfa_setup(db, setup_token=body.setup_token)
        elif user:
            result = await init_mfa_setup(db, user=user)
        else:
            raise AuthError("NOT_AUTHENTICATED", 401)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status, detail={"code": exc.code}) from exc

    return ApiResponse(success=True, data=result)


@router.post("/mfa/setup/confirm", response_model=ApiResponse)
async def mfa_setup_confirm(
    body: MfaSetupConfirmRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    try:
        if body.setup_token:
            result = await confirm_mfa_setup(
                db,
                setup_token=body.setup_token,
                code=body.code,
                ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                client_hint=request.headers.get("x-client-hint", ""),
            )
        elif user:
            result = await confirm_mfa_setup(
                db,
                user=user,
                code=body.code,
                ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                client_hint=request.headers.get("x-client-hint", ""),
            )
        else:
            raise AuthError("NOT_AUTHENTICATED", 401)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status, detail={"code": exc.code}) from exc

    if result.get("access_token"):
        _set_refresh_cookie(response, result["refresh_token"])
        return ApiResponse(
            success=True,
            data=TokenResponse(
                access_token=result["access_token"],
                expires_at=result["expires_at"],
            ).model_dump(),
        )

    return ApiResponse(success=True, data={"mfa_enabled": True})


@router.post("/refresh", response_model=ApiResponse)
>>>>>>> main
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
<<<<<<< HEAD
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
=======
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    if not refresh_token:
        raise HTTPException(status_code=401, detail={"code": "NO_REFRESH_TOKEN"})

    try:
        result = await refresh_access_token(
            db,
            refresh_token=refresh_token,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except AuthError as exc:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=exc.status, detail={"code": exc.code}) from exc

    _set_refresh_cookie(response, result["refresh_token"])
    return ApiResponse(
        success=True,
        data=TokenResponse(
            access_token=result["access_token"],
            expires_at=result["expires_at"],
        ).model_dump(),
    )


@router.post("/logout", response_model=ApiResponse)
async def logout_endpoint(
    request: Request,
    response: Response,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    access_jti = None
    access_exp = None
    if credentials:
        try:
            payload = verify_access_token(credentials.credentials)
            access_jti = payload.get("jti")
            access_exp = payload.get("exp")
        except ValueError:
            pass

    refresh_token = request.cookies.get(REFRESH_COOKIE)
    if refresh_token:
        await logout(
            db,
            refresh_token=refresh_token,
            access_jti=access_jti,
            access_exp=access_exp,
        )
        await db.commit()
    _clear_refresh_cookie(response)
    return ApiResponse(success=True, data={"logged_out": True})


@router.post("/parent/request-otp", response_model=ApiResponse)
async def parent_request_otp(
    body: ParentOtpRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await request_parent_otp(
            db,
            phone=body.phone,
            ip=request.client.host if request.client else None,
        )
    except AuthError as exc:
        raise HTTPException(status_code=exc.status, detail={"code": exc.code}) from exc
    return ApiResponse(success=True, data=result)


@router.post("/parent/verify-otp", response_model=ApiResponse)
async def parent_verify_otp(
    body: ParentOtpVerifyRequest,
>>>>>>> main
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    try:
<<<<<<< HEAD
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
=======
        result = await verify_parent_otp(
            db,
            phone=body.phone,
            otp=body.otp,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            client_hint=request.headers.get("x-client-hint", ""),
        )
    except AuthError as exc:
        raise HTTPException(status_code=exc.status, detail={"code": exc.code}) from exc

    _set_refresh_cookie(response, result["refresh_token"])
    return ApiResponse(
        success=True,
        data=TokenResponse(
            access_token=result["access_token"],
            expires_at=result["expires_at"],
        ).model_dump(),
    )


@router.post("/change-password", response_model=ApiResponse)
async def change_password_endpoint(
    body: ChangePasswordRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    payload = getattr(request.state, "token_payload", {})
    try:
        await change_password(
            db,
            user,
            current_password=body.current_password,
            new_password=body.new_password,
            access_jti=payload.get("jti"),
            access_exp=payload.get("exp"),
        )
        await db.commit()
    except AuthError as exc:
        raise HTTPException(status_code=exc.status, detail={"code": exc.code}) from exc
    return ApiResponse(success=True, data={"password_changed": True})


@router.post("/admin/reset-password", response_model=ApiResponse)
async def admin_reset_password_endpoint(
    body: AdminResetPasswordRequest,
    user: User = Depends(requires_permission("users.password_reset")),
    db: AsyncSession = Depends(get_db),
):
    try:
        await admin_reset_password(
            db,
            user,
            username=body.username,
            new_password=body.new_password,
        )
        await db.commit()
    except AuthError as exc:
        raise HTTPException(status_code=exc.status, detail={"code": exc.code}) from exc
    return ApiResponse(success=True, data={"username": body.username, "password_reset": True})


@router.get("/me", response_model=ApiResponse)
async def me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    permissions = await get_user_permissions(user)
    return ApiResponse(
        success=True,
        data=UserMeResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            role=user.role.code,
            center_id=user.center_id,
            locale_preference=user.locale_preference,
            permissions=permissions,
            mfa_enabled=user.mfa_enabled,
            mfa_required=user.role.code in MANDATORY_MFA_ROLES,
            mfa_configured=bool(user.mfa_secret_encrypted),
        ).model_dump(),
>>>>>>> main
    )
