from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TeacherCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    center_id: UUID
    full_name: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    specialization: str | None = None
    years_of_experience: int = Field(default=0, ge=0)
    start_date: date | None = None
    subject_ids: list[UUID] = Field(default_factory=list)


class TeacherUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = None
    specialization: str | None = None
    years_of_experience: int | None = Field(default=None, ge=0)
    start_date: date | None = None
    is_active: bool | None = None
    subject_ids: list[UUID] | None = None


class TeacherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    center_id: UUID
    full_name: str
    phone: str | None
    specialization: str | None
    years_of_experience: int
    start_date: date | None
    is_active: bool
    subject_ids: list[UUID] = []
