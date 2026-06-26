from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GroupCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    center_id: UUID
    subject_id: UUID
    name: str = Field(min_length=1, max_length=100)
    teacher_id: UUID | None = None
    room: str | None = Field(default=None, max_length=100)
    schedule_json: dict | None = None
    start_date: date | None = None
    end_date: date | None = None


class GroupUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=100)
    subject_id: UUID | None = None
    teacher_id: UUID | None = None
    room: str | None = None
    schedule_json: dict | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class GroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    center_id: UUID
    subject_id: UUID
    name: str
    teacher_id: UUID | None
    room: str | None
    schedule_json: dict | None
    start_date: date | None
    end_date: date | None
    is_active: bool
    enrollment_count: int = 0
    subject_name_uz: str | None = None
    teacher_name: str | None = None


class EnrollmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: UUID


class EnrollmentBatchCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_ids: list[UUID] = Field(min_length=1, max_length=50)


class EnrollmentMemberResponse(BaseModel):
    enrollment_id: UUID
    student_id: UUID
    full_name: str
    grade: str | None = None


class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name_uz: str
    name_ru: str
    name_en: str
    is_active: bool
