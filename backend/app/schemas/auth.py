from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    success: bool
    data: Any = None
    meta: dict | None = None
    error: dict | None = None


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class MfaVerifyRequest(BaseModel):
    mfa_token: str
    code: str = Field(..., min_length=6, max_length=8)


class OtpRequestBody(BaseModel):
    phone: str = Field(..., pattern=r"^\+998\d{9}$")


class OtpVerifyRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+998\d{9}$")
    code: str = Field(..., min_length=6, max_length=6)


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=12)


class MfaSetupResponse(BaseModel):
    secret: str
    provisioning_uri: str
    backup_codes: list[str]


class UserResponse(BaseModel):
    id: UUID
    username: str | None
    email: str | None
    phone: str | None
    role: str
    role_name_uz: str
    role_name_ru: str
    role_name_en: str
    center_id: UUID | None
    locale_preference: str
    mfa_enabled: bool
    must_change_password: bool
    permissions: list[str]

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str | None = None
    token_type: str = "bearer"
    mfa_required: bool = False
    mfa_token: str | None = None
    must_change_password: bool = False
    user: UserResponse | None = None


class LocaleUpdateRequest(BaseModel):
    locale: str = Field(..., pattern=r"^(uz|ru|en)$")
