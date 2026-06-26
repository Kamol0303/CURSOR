from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CenterCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    stir: str | None = Field(default=None, pattern=r"^\d{9}$")
    director_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=255)
    address: str | None = None
    license_number: str | None = Field(default=None, max_length=100)
    license_expiry: datetime | None = None
    center_type: str = Field(default="private", pattern=r"^(private|public)$")
    mahalla_id: UUID | None = None


class CenterUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    stir: str | None = Field(default=None, pattern=r"^\d{9}$")
    director_name: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    license_number: str | None = None
    license_expiry: datetime | None = None
    center_type: str | None = Field(default=None, pattern=r"^(private|public)$")
    is_active: bool | None = None
    mahalla_id: UUID | None = None


class CenterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    stir: str | None
    director_name: str | None
    phone: str | None
    email: str | None
    address: str | None
    license_number: str | None
    license_expiry: datetime | None
    center_type: str
    is_active: bool
    mahalla_id: UUID | None
