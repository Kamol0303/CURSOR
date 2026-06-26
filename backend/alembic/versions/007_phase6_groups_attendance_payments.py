"""Phase 6 — groups schedule fields, attendance, payments foundation

Revision ID: 007_phase6
Revises: 006_analytics_grants
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007_phase6"
down_revision: Union[str, None] = "006_analytics_grants"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("groups", sa.Column("room", sa.String(100), nullable=True))
    op.add_column("groups", sa.Column("schedule_json", postgresql.JSONB(), nullable=True))
    op.add_column("groups", sa.Column("start_date", sa.Date(), nullable=True))
    op.add_column("groups", sa.Column("end_date", sa.Date(), nullable=True))
    op.add_column("groups", sa.Column("is_active", sa.Boolean(), server_default="true"))

    op.create_table(
        "attendance_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("session_date", sa.Date(), nullable=False),
        sa.Column("qr_token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_attendance_sessions_group_date", "attendance_sessions", ["group_id", "session_date"])

    op.create_table(
        "attendance_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("session_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("method", sa.String(20), server_default="manual"),
        sa.Column("marked_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("student_id", "group_id", "session_date", name="uq_attendance_student_group_date"),
    )

    op.create_table(
        "student_payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="UZS"),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payment_method", sa.String(30), nullable=True),
        sa.Column("external_transaction_id", sa.String(128), nullable=True),
        sa.Column("discount_percent", sa.Float(), server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_student_payments_student", "student_payments", ["student_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_student_payments_student", "student_payments")
    op.drop_table("student_payments")
    op.drop_table("attendance_records")
    op.drop_index("ix_attendance_sessions_group_date", "attendance_sessions")
    op.drop_table("attendance_sessions")
    op.drop_column("groups", "is_active")
    op.drop_column("groups", "end_date")
    op.drop_column("groups", "start_date")
    op.drop_column("groups", "schedule_json")
    op.drop_column("groups", "room")
