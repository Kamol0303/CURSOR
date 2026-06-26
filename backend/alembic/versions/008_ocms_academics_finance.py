"""OCMS — courses, exams, grades, transactions, files, messages

Revision ID: 008_ocms
Revises: 007_phase6
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "008_ocms"
down_revision: Union[str, None] = "007_phase6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("groups", sa.Column("max_students", sa.Integer(), nullable=True))
    op.add_column("students", sa.Column("photo_file_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("students", sa.Column("passport_json", postgresql.JSONB(), nullable=True))
    op.add_column("teachers", sa.Column("monthly_salary", sa.Numeric(12, 2), nullable=True))
    op.add_column("teachers", sa.Column("kpi_score", sa.Float(), server_default="0"))
    op.add_column("teachers", sa.Column("rating_score", sa.Float(), server_default="0"))

    op.create_table(
        "courses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subjects.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("duration_weeks", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_courses_center", "courses", ["center_id"])

    op.create_table(
        "lessons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id"), nullable=True),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), server_default="90"),
        sa.Column("room", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "exams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subjects.id"), nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id"), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("pass_score", sa.Float(), server_default="60"),
        sa.Column("duration_minutes", sa.Integer(), server_default="60"),
        sa.Column("is_published", sa.Boolean(), server_default="false"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_exams_center", "exams", ["center_id", "is_published"])

    op.create_table(
        "exam_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("exam_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("options_json", postgresql.JSONB(), nullable=True),
        sa.Column("correct_answer", sa.String(500), nullable=False),
        sa.Column("points", sa.Float(), server_default="1"),
        sa.Column("order_index", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "exam_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("exam_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exams.id"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("score", sa.Float(), server_default="0"),
        sa.Column("max_score", sa.Float(), server_default="0"),
        sa.Column("passed", sa.Boolean(), server_default="false"),
        sa.Column("answers_json", postgresql.JSONB(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("exam_id", "student_id", name="uq_exam_result_student"),
    )

    op.create_table(
        "grades",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id"), nullable=True),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subjects.id"), nullable=False),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("grade_value", sa.Float(), nullable=False),
        sa.Column("grade_type", sa.String(30), server_default="monthly"),
        sa.Column("term", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("graded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("graded_at", sa.Date(), server_default=sa.text("CURRENT_DATE")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_grades_student", "grades", ["student_id", "subject_id"])

    op.create_table(
        "payment_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("student_payments.id"), nullable=False),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("external_id", sa.String(128), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_payment_tx_external", "payment_transactions", ["provider", "external_id"])

    op.create_table(
        "files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("owner_type", sa.String(50), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), server_default="0"),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_files_owner", "files", ["owner_type", "owner_id"])

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("recipient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("channel", sa.String(20), server_default="in_app"),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default="false"),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # New RBAC roles
    op.execute(
        """
        INSERT INTO roles (id, code, name_uz, name_ru, name_en, created_at, updated_at)
        SELECT gen_random_uuid(), 'accountant', 'Buxgalter', 'Бухгалтер', 'Accountant', now(), now()
        WHERE NOT EXISTS (SELECT 1 FROM roles WHERE code = 'accountant')
        """
    )
    op.execute(
        """
        INSERT INTO roles (id, code, name_uz, name_ru, name_en, created_at, updated_at)
        SELECT gen_random_uuid(), 'student', 'O''quvchi', 'Учащийся', 'Student', now(), now()
        WHERE NOT EXISTS (SELECT 1 FROM roles WHERE code = 'student')
        """
    )


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_index("ix_files_owner", "files")
    op.drop_table("files")
    op.drop_index("ix_payment_tx_external", "payment_transactions")
    op.drop_table("payment_transactions")
    op.drop_index("ix_grades_student", "grades")
    op.drop_table("grades")
    op.drop_table("exam_results")
    op.drop_table("exam_questions")
    op.drop_index("ix_exams_center", "exams")
    op.drop_table("exams")
    op.drop_table("lessons")
    op.drop_index("ix_courses_center", "courses")
    op.drop_table("courses")
    op.drop_column("teachers", "rating_score")
    op.drop_column("teachers", "kpi_score")
    op.drop_column("teachers", "monthly_salary")
    op.drop_column("students", "passport_json")
    op.drop_column("students", "photo_file_id")
    op.drop_column("groups", "max_students")
