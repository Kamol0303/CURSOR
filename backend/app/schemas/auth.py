<<<<<<< HEAD
from __future__ import annotations
=======
from datetime import datetime
from uuid import UUID
>>>>>>> main

from pydantic import BaseModel, ConfigDict, Field


<<<<<<< HEAD
class LoginRequest(BaseModel):
    username: str
    password: str
    locale: str | None = None


class MFAChallengeRequest(BaseModel):
    challenge_token: str
    code: str = Field(min_length=6, max_length=12)


class ParentOTPRequest(BaseModel):
    phone: str


class ParentOTPVerifyRequest(BaseModel):
    phone: str
    code: str = Field(min_length=6, max_length=6)


class RefreshRequest(BaseModel):
    refresh_token: str | None = None


class LoginResult(BaseModel):
    access_token: str | None = None
    token_type: str | None = "bearer"
    expires_in: int | None = None
    mfa_required: bool = False
    challenge_token: str | None = None
    must_change_password: bool = False
    user: "UserSummary | None" = None


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str | None
    # Plain string (not EmailStr): internal/demo domains such as ``*.local`` are
    # valid identifiers here and must not fail serialization of stored data.
    email: str | None = None
    phone: str | None = None
    role: str
    center_id: str | None
    locale_preference: str
    mfa_enabled: bool


class MeResponse(BaseModel):
    user: UserSummary
    permissions: list[str]


class LogoutRequest(BaseModel):
    refresh_token: str | None = None
=======
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
    code: str = Field(min_length=6, max_length=8)


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
>>>>>>> main
