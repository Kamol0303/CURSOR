from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    center_id: UUID | None = None
    subject_id: UUID
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price: float | None = Field(default=None, ge=0)
    duration_weeks: int | None = Field(default=None, ge=1)


class CourseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: float | None = Field(default=None, ge=0)
    duration_weeks: int | None = Field(default=None, ge=1)
    is_active: bool | None = None
    subject_id: UUID | None = None


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    center_id: UUID
    subject_id: UUID
    name: str
    description: str | None
    price: float | None
    duration_weeks: int | None
    is_active: bool
    lesson_count: int = 0
    subject_name_uz: str | None = None


class LessonCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    scheduled_at: datetime | None = None
    duration_minutes: int = Field(default=90, ge=15, le=480)
    room: str | None = Field(default=None, max_length=100)
    group_id: UUID | None = None


class LessonUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    scheduled_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, ge=15, le=480)
    room: str | None = None
    group_id: UUID | None = None


class LessonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    course_id: UUID
    center_id: UUID
    title: str
    scheduled_at: datetime | None
    duration_minutes: int
    room: str | None
    group_id: UUID | None
