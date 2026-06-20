from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StudentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    center_id: UUID
    full_name: str = Field(min_length=1, max_length=255)
    jshshir: str | None = Field(default=None, pattern=r"^\d{14}$")
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, pattern=r"^(male|female)$")
    phone: str | None = None
    address: str | None = None
    school: str | None = None
    grade: str | None = None
    enrollment_date: date | None = None
    guardian_name: str | None = None
    guardian_phone: str | None = Field(default=None, pattern=r"^\+998\d{9}$")


class StudentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, pattern=r"^(male|female)$")
    phone: str | None = None
    address: str | None = None
    school: str | None = None
    grade: str | None = None
    enrollment_date: date | None = None


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    center_id: UUID
    full_name: str
    jshshir_masked: str | None = None
    date_of_birth: date | None
    gender: str | None
    phone: str | None
    address: str | None
    school: str | None
    grade: str | None
    enrollment_date: date | None
    graduation_date: date | None
    consent_given_at: datetime | None
