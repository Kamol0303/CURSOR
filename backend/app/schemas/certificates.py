from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CertificateCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: UUID
    title: str = Field(min_length=1, max_length=255)
    issue_date: date
    file_id: UUID
    subject_id: UUID | None = None
