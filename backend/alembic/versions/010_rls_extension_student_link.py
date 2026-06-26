"""RLS extension for OCMS tables and students.user_id link.

Revision ID: 010_rls_extension
Revises: 009_payment_tx_unique
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "010_rls_extension"
down_revision: Union[str, None] = "009_payment_tx_unique"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CENTER_POLICY = """
    current_setting('app.role', true) IN ('super_admin', 'hokimiyat_operator', 'auditor', 'system')
    OR (
        current_setting('app.center_id', true) <> ''
        AND center_id = NULLIF(current_setting('app.center_id', true), '')::uuid
    )
"""

_STUDENT_ROW_POLICY = f"""
    {_CENTER_POLICY}
    OR (
        current_setting('app.role', true) = 'student'
        AND current_setting('app.student_id', true) <> ''
        AND student_id = NULLIF(current_setting('app.student_id', true), '')::uuid
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
"""

_RLS_TABLES_CENTER = [
    "courses",
    "lessons",
    "exams",
    "groups",
    "teachers",
    "files",
    "attendance_sessions",
    "student_payments",
]

_RLS_TABLES_STUDENT = [
    "exam_results",
    "grades",
    "attendance_records",
]


def _enable_rls(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")


def upgrade() -> None:
    op.add_column(
        "students",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_students_user_id", "students", ["user_id"], unique=True)

    for table in _RLS_TABLES_CENTER:
        _enable_rls(table)
        op.execute(f"""
            CREATE POLICY {table}_rls ON {table}
            USING ({_CENTER_POLICY})
        """)

    for table in _RLS_TABLES_STUDENT:
        _enable_rls(table)
        op.execute(f"""
            CREATE POLICY {table}_rls ON {table}
            USING ({_STUDENT_ROW_POLICY})
        """)


def downgrade() -> None:
    for table in _RLS_TABLES_CENTER + _RLS_TABLES_STUDENT:
        op.execute(f"DROP POLICY IF EXISTS {table}_rls ON {table}")
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    op.drop_index("ix_students_user_id", table_name="students")
    op.drop_column("students", "user_id")
