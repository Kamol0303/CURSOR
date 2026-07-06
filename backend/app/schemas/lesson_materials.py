from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LessonGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject_id: UUID
    topic: str = Field(min_length=2, max_length=500)
    content_type: str = Field(pattern="^(presentation|game)$")
    group_id: UUID | None = None
    locale: str | None = None


class LessonMaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    center_id: UUID
    teacher_id: UUID
    group_id: UUID | None
    subject_id: UUID
    subject_name_uz: str | None = None
    topic: str
    content_type: str
    locale: str
    title: str
    content_json: dict
    status: str
    ai_provider: str | None
    started_at: datetime | None
    created_at: datetime | None = None


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None
    username: str | None = None
    user_role: str | None = None
    action: str
    resource_type: str
    resource_id: UUID | None
    details: dict | None
    ip_address: str | None
    created_at: datetime
