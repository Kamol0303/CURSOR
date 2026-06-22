from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: UUID
    center_id: UUID
    amount: float = Field(gt=0)
    currency: str = Field(default="UZS", max_length=3)
    due_date: date | None = None
    discount_percent: float = Field(default=0, ge=0, le=100)
    notes: str | None = None


class PaymentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str | None = Field(default=None, pattern=r"^(pending|paid|overdue|cancelled)$")
    paid_at: datetime | None = None
    payment_method: str | None = None
    external_transaction_id: str | None = None
    discount_percent: float | None = Field(default=None, ge=0, le=100)
    notes: str | None = None


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID
    center_id: UUID
    amount: float
    currency: str
    status: str
    due_date: date | None
    paid_at: datetime | None
    payment_method: str | None
    discount_percent: float
    student_name: str | None = None
