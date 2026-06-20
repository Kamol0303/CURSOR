from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.identity import User
from app.schemas.auth import (
    ApiResponse,
    LoginRequest,
    MfaVerifyRequest,
    TokenResponse,
    UserMeResponse,
)
from app.services.auth_service import (
    AuthError,
    get_user_permissions,
    login_with_password,
    logout,
    refresh_access_token,
    verify_mfa_and_issue_tokens,
)

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "tamor_refresh"


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
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    try:
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
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    try:
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


@router.post("/refresh", response_model=ApiResponse)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
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
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    if refresh_token:
        await logout(db, refresh_token=refresh_token)
    _clear_refresh_cookie(response)
    return ApiResponse(success=True, data={"logged_out": True})


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
        ).model_dump(),
    )
