from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    meta: dict | None = None
    error: dict | None = None


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=128)


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)


class AdminResetPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=100)
    new_password: str = Field(min_length=12, max_length=128)


class MfaVerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mfa_token: str = Field(min_length=1, max_length=128)
    code: str = Field(min_length=6, max_length=12)


class MfaSetupInitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    setup_token: str | None = Field(default=None, max_length=128)


class MfaSetupConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=6, max_length=8)
    setup_token: str | None = Field(default=None, max_length=128)


class MfaSetupInitResponse(BaseModel):
    provisioning_uri: str
    secret: str
    issuer: str
    setup_token: str | None = None


class ParentOtpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phone: str = Field(pattern=r"^\+998\d{9}$")


class ParentOtpVerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phone: str = Field(pattern=r"^\+998\d{9}$")
    otp: str = Field(min_length=4, max_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    requires_mfa: bool = False
    mfa_token: str | None = None


class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str | None
    email: str | None
    phone: str | None
    role: str
    center_id: UUID | None
    locale_preference: str
    permissions: list[str]
    mfa_enabled: bool
    mfa_required: bool = False
    mfa_configured: bool = False
