"""Phase 2 — ratings, certificates, reports

Revision ID: 003_phase2
Revises: 002_phase1
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_phase2"
down_revision: Union[str, None] = "002_phase1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rating_formula_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("weights", postgresql.JSONB(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    op.create_table(
        "rating_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column(
            "formula_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rating_formula_versions.id"),
            nullable=False,
        ),
        sa.Column("period", sa.Date(), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("rank_change", sa.Integer(), nullable=True),
        sa.Column("criteria_breakdown", postgresql.JSONB(), nullable=False),
        sa.Column("inputs_hash", sa.String(64), nullable=False),
        sa.Column("flagged_anomaly", sa.Boolean(), server_default="false"),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_rating_history_center_period", "rating_history", ["center_id", "period"])

    op.create_table(
        "certificates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("certificate_number", sa.String(50), unique=True, nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subjects.id"), nullable=True),
        sa.Column("course_name_uz", sa.String(255), nullable=False),
        sa.Column("course_name_ru", sa.String(255), nullable=False),
        sa.Column("course_name_en", sa.String(255), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), server_default="valid"),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoke_reason", sa.Text(), nullable=True),
        sa.Column("integrity_hash", sa.String(64), nullable=False),
        sa.Column("idempotency_key", sa.String(64), unique=True, nullable=True),
        sa.Column("locale", sa.String(5), server_default="uz"),
        sa.Column("is_demo_data", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_certificates_number", "certificates", ["certificate_number"])

    op.create_table(
        "certificate_verifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("certificate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("certificates.id"), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("result", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("parameters", postgresql.JSONB(), nullable=False),
        sa.Column("locale", sa.String(5), server_default="uz"),
        sa.Column("file_format", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), server_default="completed"),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("certificate_verifications")
    op.drop_index("ix_certificates_number", "certificates")
    op.drop_table("certificates")
    op.drop_index("ix_rating_history_center_period", "rating_history")
    op.drop_table("rating_history")
    op.drop_table("rating_formula_versions")
