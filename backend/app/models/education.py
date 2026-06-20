import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.identity import TimestampMixin, TrainingCenter


class Region(Base, TimestampMixin):
    __tablename__ = "regions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_uz: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)

    mahallas: Mapped[list["Mahalla"]] = relationship(back_populates="region")


class Mahalla(Base, TimestampMixin):
    __tablename__ = "mahallas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("regions.id"), nullable=False)
    name_uz: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)

    region: Mapped["Region"] = relationship(back_populates="mahallas")
    centers: Mapped[list["TrainingCenter"]] = relationship(back_populates="mahalla")


class Subject(Base, TimestampMixin):
    __tablename__ = "subjects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_uz: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    groups: Mapped[list["Group"]] = relationship(back_populates="subject")
    teacher_subjects: Mapped[list["TeacherSubject"]] = relationship(back_populates="subject")


class Group(Base, TimestampMixin):
    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    center_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("training_centers.id"), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    teacher_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=True)

    center: Mapped["TrainingCenter"] = relationship(back_populates="groups")
    subject: Mapped["Subject"] = relationship(back_populates="groups")
    teacher: Mapped["Teacher | None"] = relationship(back_populates="groups")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="group")


class Teacher(Base, TimestampMixin):
    __tablename__ = "teachers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    center_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("training_centers.id"), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    specialization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    years_of_experience: Mapped[int] = mapped_column(Integer, default=0)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=False)

    center: Mapped["TrainingCenter"] = relationship(back_populates="teachers")
    groups: Mapped[list["Group"]] = relationship(back_populates="teacher")
    teacher_subjects: Mapped[list["TeacherSubject"]] = relationship(back_populates="teacher")


class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"

    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teachers.id"), primary_key=True)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("subjects.id"), primary_key=True)

    teacher: Mapped["Teacher"] = relationship(back_populates="teacher_subjects")
    subject: Mapped["Subject"] = relationship(back_populates="teacher_subjects")


class Student(Base, TimestampMixin):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    center_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("training_centers.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    jshshir_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    school: Mapped[str | None] = mapped_column(String(255), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    enrollment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    graduation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    consent_given_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=False)

    center: Mapped["TrainingCenter"] = relationship(back_populates="students")
    guardians: Mapped[list["Guardian"]] = relationship(back_populates="student")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="student")


class Guardian(Base, TimestampMixin):
    __tablename__ = "guardians"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), default="parent")

    student: Mapped["Student"] = relationship(back_populates="guardians")


class Enrollment(Base, TimestampMixin):
    __tablename__ = "enrollments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    center_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("training_centers.id"), nullable=False)
    enrolled_at: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    status: Mapped[str] = mapped_column(String(20), default="active")

    student: Mapped["Student"] = relationship(back_populates="enrollments")
    group: Mapped["Group"] = relationship(back_populates="enrollments")
    center: Mapped["TrainingCenter"] = relationship(back_populates="enrollments")
