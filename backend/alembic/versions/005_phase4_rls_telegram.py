"""Migration 005 — RLS policies, telegram subscriptions, parent portal support

Revision ID: 005_phase4
Revises: 004_phase3
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005_phase4"
down_revision: Union[str, None] = "004_phase3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "telegram_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chat_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("locale", sa.String(5), server_default="uz"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Row-Level Security (defense-in-depth per ADR-006)
    op.execute("ALTER TABLE students ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE certificates ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE guardians ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE students FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE enrollments FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE certificates FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE guardians FORCE ROW LEVEL SECURITY")

    op.execute("""
        CREATE POLICY students_rls ON students
        USING (
            current_setting('app.role', true) IN ('super_admin', 'hokimiyat_operator', 'auditor', 'system')
            OR (
                current_setting('app.center_id', true) <> ''
                AND center_id = NULLIF(current_setting('app.center_id', true), '')::uuid
            )
            OR (
                current_setting('app.role', true) = 'parent'
                AND current_setting('app.phone', true) <> ''
                AND id IN (
                    SELECT student_id FROM guardians
                    WHERE phone = current_setting('app.phone', true)
                    AND deleted_at IS NULL
                )
            )
        )
    """)

    op.execute("""
        CREATE POLICY enrollments_rls ON enrollments
        USING (
            current_setting('app.role', true) IN ('super_admin', 'hokimiyat_operator', 'auditor', 'system')
            OR (
                current_setting('app.center_id', true) <> ''
                AND center_id = NULLIF(current_setting('app.center_id', true), '')::uuid
            )
            OR (
                current_setting('app.role', true) = 'parent'
                AND current_setting('app.phone', true) <> ''
                AND student_id IN (
                    SELECT student_id FROM guardians
                    WHERE phone = current_setting('app.phone', true)
                    AND deleted_at IS NULL
                )
            )
        )
    """)

    op.execute("""
        CREATE POLICY certificates_rls ON certificates
        USING (
            current_setting('app.role', true) IN ('super_admin', 'hokimiyat_operator', 'auditor', 'system', 'verifier')
            OR (
                current_setting('app.center_id', true) <> ''
                AND center_id = NULLIF(current_setting('app.center_id', true), '')::uuid
            )
            OR (
                current_setting('app.role', true) = 'parent'
                AND current_setting('app.phone', true) <> ''
                AND student_id IN (
                    SELECT student_id FROM guardians
                    WHERE phone = current_setting('app.phone', true)
                    AND deleted_at IS NULL
                )
            )
        )
    """)

    op.execute("""
        CREATE POLICY guardians_rls ON guardians
        USING (
            current_setting('app.role', true) IN ('super_admin', 'hokimiyat_operator', 'auditor', 'system')
            OR (
                current_setting('app.center_id', true) <> ''
                AND student_id IN (
                    SELECT id FROM students
                    WHERE center_id = NULLIF(current_setting('app.center_id', true), '')::uuid
                    AND deleted_at IS NULL
                )
            )
            OR (
                current_setting('app.role', true) = 'parent'
                AND current_setting('app.phone', true) <> ''
                AND phone = current_setting('app.phone', true)
            )
        )
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS guardians_rls ON guardians")
    op.execute("DROP POLICY IF EXISTS certificates_rls ON certificates")
    op.execute("DROP POLICY IF EXISTS enrollments_rls ON enrollments")
    op.execute("DROP POLICY IF EXISTS students_rls ON students")

    op.execute("ALTER TABLE guardians DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE certificates DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE enrollments DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE students DISABLE ROW LEVEL SECURITY")

    op.drop_table("telegram_subscriptions")
