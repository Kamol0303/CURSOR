from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.deps import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.auth import (
    APIResponse,
    LocaleUpdateRequest,
    LoginRequest,
    LoginResponse,
    MfaVerifyRequest,
    OtpRequestBody,
    OtpVerifyRequest,
    PasswordChangeRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

REFRESH_COOKIE = "tamor_refresh_token"


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=not settings.debug,
        samesite="strict",
        max_age=settings.jwt_refresh_token_expire_days * 86400,
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE, path="/api/v1/auth")


@router.post("/login", response_model=APIResponse)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    result = await service.login(body.username, body.password, ip, user_agent)

    if "error" in result:
        return APIResponse(success=False, error={"code": result["error"], "field": None})

    if result.get("mfa_required"):
        return APIResponse(
            success=True,
            data=LoginResponse(
                mfa_required=True,
                mfa_token=result["mfa_token"],
                must_change_password=result.get("must_change_password", False),
            ),
        )

    _set_refresh_cookie(response, result["refresh_token"])
    return APIResponse(
        success=True,
        data=LoginResponse(
            access_token=result["access_token"],
            user=result["user"],
            must_change_password=result.get("must_change_password", False),
        ),
    )


@router.post("/mfa/verify", response_model=APIResponse)
async def verify_mfa(
    body: MfaVerifyRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    result = await service.verify_mfa(body.mfa_token, body.code, ip, user_agent)

    if "error" in result:
        return APIResponse(success=False, error={"code": result["error"], "field": None})

    _set_refresh_cookie(response, result["refresh_token"])
    return APIResponse(
        success=True,
        data=LoginResponse(
            access_token=result["access_token"],
            user=result["user"],
            must_change_password=result.get("must_change_password", False),
        ),
    )


@router.post("/login/otp/request", response_model=APIResponse)
async def request_otp(
    body: OtpRequestBody,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    result = await service.request_otp(body.phone)

    if "error" in result:
        return APIResponse(success=False, error={"code": result["error"], "field": "phone"})

    data = {"otp_sent": True}
    if settings.sms_provider == "console":
        data["dev_code"] = result.get("dev_code")
    return APIResponse(success=True, data=data)


@router.post("/login/otp/verify", response_model=APIResponse)
async def verify_otp(
    body: OtpVerifyRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    result = await service.verify_otp(body.phone, body.code, ip, user_agent)

    if "error" in result:
        return APIResponse(success=False, error={"code": result["error"], "field": None})

    _set_refresh_cookie(response, result["refresh_token"])
    return APIResponse(
        success=True,
        data=LoginResponse(
            access_token=result["access_token"],
            user=result["user"],
        ),
    )


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        return APIResponse(success=False, error={"code": "REFRESH_TOKEN_MISSING", "field": None})

    service = AuthService(db)
    result = await service.refresh_tokens(token)

    if "error" in result:
        _clear_refresh_cookie(response)
        return APIResponse(success=False, error={"code": result["error"], "field": None})

    _set_refresh_cookie(response, result["refresh_token"])
    return APIResponse(
        success=True,
        data={"access_token": result["access_token"], "token_type": "bearer"},
    )


@router.post("/logout", response_model=APIResponse)
async def logout(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    token = request.cookies.get(REFRESH_COOKIE)
    if token:
        service = AuthService(db)
        await service.logout(token)
    _clear_refresh_cookie(response)
    return APIResponse(success=True, data={"logged_out": True})


@router.get("/me", response_model=APIResponse)
async def get_me(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    return APIResponse(success=True, data=service._user_response(user))


@router.post("/mfa/setup", response_model=APIResponse)
async def setup_mfa(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    result = await service.setup_mfa(user)
    return APIResponse(success=True, data=result)


@router.post("/password/change", response_model=APIResponse)
async def change_password(
    body: PasswordChangeRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    result = await service.change_password(user, body.current_password, body.new_password)

    if "error" in result:
        return APIResponse(success=False, error={"code": result["error"], "field": "password"})

    return APIResponse(success=True, data={"password_changed": True})


@router.patch("/locale", response_model=APIResponse)
async def update_locale(
    body: LocaleUpdateRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user.locale_preference = body.locale
    await db.flush()
    return APIResponse(success=True, data={"locale": body.locale})
