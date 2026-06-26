from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recipient_id: UUID
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    center_id: UUID
    sender_id: UUID | None
    recipient_id: UUID | None
    title: str
    body: str
    is_read: bool
    sent_at: datetime
    sender_name: str | None = None
    recipient_name: str | None = None


class MessageRecipientResponse(BaseModel):
    id: str
    display_name: str
    role: str
    username: str | None = None


class MessageMonitorResponse(BaseModel):
    id: UUID
    center_id: UUID
    center_name: str
    sender_id: UUID | None
    recipient_id: UUID | None
    sender_name: str | None
    recipient_name: str | None
    title: str
    body: str
    sent_at: datetime
