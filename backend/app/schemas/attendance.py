from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AttendanceMarkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: UUID
    group_id: UUID
    session_date: date
    status: str = Field(pattern=r"^(present|absent|late|excused)$")
    notes: str | None = None


class AttendanceRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID
    group_id: UUID
    session_date: date
    status: str
    method: str
    student_name: str | None = None


class AttendanceSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    group_id: UUID
    session_date: date
    qr_payload: str
    expires_at: str


class QrScanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    qr_payload: str
    student_id: UUID
