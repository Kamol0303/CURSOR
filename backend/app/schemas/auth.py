from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


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
