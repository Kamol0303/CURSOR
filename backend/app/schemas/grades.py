from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class GradeCreate(BaseModel):
    student_id: UUID
    subject_id: UUID
    group_id: UUID | None = None
    center_id: UUID | None = None
    grade_value: float = Field(ge=0, le=100)
    grade_type: str = "monthly"
    term: str | None = None
    notes: str | None = None


class GradeResponse(BaseModel):
    id: UUID
    student_id: UUID
    subject_id: UUID
    group_id: UUID | None
    center_id: UUID
    grade_value: float
    grade_type: str
    term: str | None
    notes: str | None
    graded_at: date
