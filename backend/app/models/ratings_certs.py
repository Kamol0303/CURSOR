from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.identity import TimestampMixin

if TYPE_CHECKING:
    from app.models.education import Student
    from app.models.identity import TrainingCenter


class RatingFormulaVersion(Base):
    __tablename__ = "rating_formula_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    weights: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    rating_history: Mapped[list["RatingHistory"]] = relationship(back_populates="formula_version")


class RatingHistory(Base):
    __tablename__ = "rating_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    center_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("training_centers.id"), nullable=False)
    formula_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rating_formula_versions.id"), nullable=False
    )
    period: Mapped[date] = mapped_column(Date, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rank_change: Mapped[int | None] = mapped_column(Integer, nullable=True)
    criteria_breakdown: Mapped[dict] = mapped_column(JSONB, nullable=False)
    inputs_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    flagged_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    center: Mapped["TrainingCenter"] = relationship("TrainingCenter", back_populates="rating_history")
    formula_version: Mapped["RatingFormulaVersion"] = relationship(back_populates="rating_history")


class Certificate(Base, TimestampMixin):
    __tablename__ = "certificates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    center_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("training_centers.id"), nullable=False)
    subject_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    course_name_uz: Mapped[str] = mapped_column(String(255), nullable=False)
    course_name_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    course_name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="valid")
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoke_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    integrity_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    locale: Mapped[str] = mapped_column(String(5), default="uz")
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=False)

    student: Mapped["Student"] = relationship("Student", back_populates="certificates")
    center: Mapped["TrainingCenter"] = relationship("TrainingCenter", back_populates="certificates")
    verifications: Mapped[list["CertificateVerification"]] = relationship(back_populates="certificate")


class CertificateVerification(Base):
    __tablename__ = "certificate_verifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    certificate: Mapped["Certificate"] = relationship(back_populates="verifications")


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    requested_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False)
    locale: Mapped[str] = mapped_column(String(5), default="uz")
    file_format: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
