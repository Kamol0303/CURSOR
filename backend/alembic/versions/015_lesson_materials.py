"""Revision ID: 015_lesson_materials
Revises: 014_certificate_file_id
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "015_lesson_materials"
down_revision: Union[str, None] = "014_certificate_file_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lesson_materials",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_centers.id"), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id"), nullable=True),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subjects.id"), nullable=False),
        sa.Column("topic", sa.String(500), nullable=False),
        sa.Column("content_type", sa.String(20), nullable=False),
        sa.Column("locale", sa.String(5), server_default="uz", nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content_json", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(20), server_default="draft", nullable=False),
        sa.Column("ai_provider", sa.String(30), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_lesson_materials_center_id", "lesson_materials", ["center_id"])
    op.create_index("ix_lesson_materials_teacher_id", "lesson_materials", ["teacher_id"])
    op.create_index("ix_lesson_materials_created_at", "lesson_materials", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_lesson_materials_created_at", table_name="lesson_materials")
    op.drop_index("ix_lesson_materials_teacher_id", table_name="lesson_materials")
    op.drop_index("ix_lesson_materials_center_id", table_name="lesson_materials")
    op.drop_table("lesson_materials")
