"""Phase 1 MVP — education entities

Revision ID: 002_phase1
Revises: 001_phase0
Create Date: 2026-06-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_phase1"
down_revision: Union[str, None] = "001_phase0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "regions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name_uz", sa.String(100), nullable=False),
        sa.Column("name_ru", sa.String(100), nullable=False),
        sa.Column("name_en", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "mahallas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("region_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("regions.id"), nullable=False),
        sa.Column("name_uz", sa.String(100), nullable=False),
        sa.Column("name_ru", sa.String(100), nullable=False),
        sa.Column("name_en", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.add_column("training_centers", sa.Column("mahalla_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("training_centers", sa.Column("is_demo_data", sa.Boolean(), server_default="false"))
    op.create_foreign_key("fk_centers_mahalla", "training_centers", "mahallas", ["mahalla_id"], ["id"])

    op.create_table(
        "subjects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name_uz", sa.String(100), nullable=False),
        sa.Column("name_ru", sa.String(100), nullable=False),
        sa.Column("name_en", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "teachers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("specialization", sa.String(255), nullable=True),
        sa.Column("years_of_experience", sa.Integer(), server_default="0"),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("is_demo_data", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_teachers_center_id", "teachers", ["center_id"])

    op.create_table(
        "teacher_subjects",
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teachers.id"), primary_key=True),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subjects.id"), primary_key=True),
    )

    op.create_table(
        "students",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("jshshir_encrypted", sa.Text(), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(10), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("school", sa.String(255), nullable=True),
        sa.Column("grade", sa.String(20), nullable=True),
        sa.Column("enrollment_date", sa.Date(), nullable=True),
        sa.Column("graduation_date", sa.Date(), nullable=True),
        sa.Column("consent_given_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_demo_data", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_students_center_id", "students", ["center_id"])

    op.create_table(
        "guardians",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("relationship_type", sa.String(50), server_default="parent"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subjects.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teachers.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("enrolled_at", sa.Date(), server_default=sa.text("CURRENT_DATE")),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_enrollments_center_id", "enrollments", ["center_id"])
    op.create_index("ix_enrollments_student_id", "enrollments", ["student_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_index("ix_enrollments_student_id", "enrollments")
    op.drop_index("ix_enrollments_center_id", "enrollments")
    op.drop_table("enrollments")
    op.drop_table("groups")
    op.drop_table("guardians")
    op.drop_index("ix_students_center_id", "students")
    op.drop_table("students")
    op.drop_table("teacher_subjects")
    op.drop_index("ix_teachers_center_id", "teachers")
    op.drop_table("teachers")
    op.drop_table("subjects")
    op.drop_constraint("fk_centers_mahalla", "training_centers", type_="foreignkey")
    op.drop_column("training_centers", "is_demo_data")
    op.drop_column("training_centers", "mahalla_id")
    op.drop_table("mahallas")
    op.drop_table("regions")
