from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    center_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("training_centers.id"), nullable=False)
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    qr_token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (UniqueConstraint("student_id", "group_id", "session_date", name="uq_attendance_student_group_date"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    center_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("training_centers.id"), nullable=False)
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    method: Mapped[str] = mapped_column(String(20), default="manual")
    marked_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class StudentPayment(Base):
    __tablename__ = "student_payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    center_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("training_centers.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="UZS")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(30), nullable=True)
    external_transaction_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    discount_percent: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
