"""Teacher-scoped RLS policies (defense-in-depth).

Revision ID: 012_teacher_rls
Revises: 011_push_subscriptions
"""

from typing import Sequence, Union

from alembic import op

revision: str = "012_teacher_rls"
down_revision: Union[str, None] = "011_push_subscriptions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TEACHER_GROUP = """
    current_setting('app.role', true) = 'teacher'
    AND current_setting('app.teacher_id', true) <> ''
    AND teacher_id = NULLIF(current_setting('app.teacher_id', true), '')::uuid
"""

_TEACHER_ENROLLMENT = """
    current_setting('app.role', true) = 'teacher'
    AND current_setting('app.teacher_id', true) <> ''
    AND group_id IN (
        SELECT id FROM groups
        WHERE teacher_id = NULLIF(current_setting('app.teacher_id', true), '')::uuid
        AND deleted_at IS NULL
    )
"""

_TEACHER_STUDENT = """
    current_setting('app.role', true) = 'teacher'
    AND current_setting('app.teacher_id', true) <> ''
    AND id IN (
        SELECT e.student_id FROM enrollments e
        JOIN groups g ON g.id = e.group_id
        WHERE g.teacher_id = NULLIF(current_setting('app.teacher_id', true), '')::uuid
        AND e.deleted_at IS NULL AND e.status = 'active'
    )
"""

_TEACHER_GROUP_ROW = """
    current_setting('app.role', true) = 'teacher'
    AND current_setting('app.teacher_id', true) <> ''
    AND group_id IN (
        SELECT id FROM groups
        WHERE teacher_id = NULLIF(current_setting('app.teacher_id', true), '')::uuid
        AND deleted_at IS NULL
    )
"""


def _replace_policy(table: str, name: str, using_expr: str) -> None:
    op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"CREATE POLICY {name} ON {table} USING ({using_expr})")


def upgrade() -> None:
    _replace_policy(
        "groups",
        "groups_rls",
        f"""
        current_setting('app.role', true) IN ('super_admin', 'hokimiyat_operator', 'auditor', 'system')
        OR (
            current_setting('app.center_id', true) <> ''
            AND center_id = NULLIF(current_setting('app.center_id', true), '')::uuid
        )
        OR ({_TEACHER_GROUP})
        """,
    )

    _replace_policy(
        "students",
        "students_rls",
        f"""
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
        OR ({_TEACHER_STUDENT})
        """,
    )

    _replace_policy(
        "enrollments",
        "enrollments_rls",
        f"""
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
        OR ({_TEACHER_ENROLLMENT})
        """,
    )

    for table in ("grades", "exam_results", "attendance_records"):
        _replace_policy(
            table,
            f"{table}_rls",
            f"""
            current_setting('app.role', true) IN ('super_admin', 'hokimiyat_operator', 'auditor', 'system')
            OR (
                current_setting('app.center_id', true) <> ''
                AND center_id = NULLIF(current_setting('app.center_id', true), '')::uuid
            )
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
            OR ({_TEACHER_GROUP_ROW})
            """,
        )


def downgrade() -> None:
    # Restore migration 010 policies (center + student/parent only for row tables)
    _CENTER = """
        current_setting('app.role', true) IN ('super_admin', 'hokimiyat_operator', 'auditor', 'system')
        OR (
            current_setting('app.center_id', true) <> ''
            AND center_id = NULLIF(current_setting('app.center_id', true), '')::uuid
        )
    """
    _replace_policy("groups", "groups_rls", _CENTER)
    op.execute("DROP POLICY IF EXISTS students_rls ON students")
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
    op.execute("DROP POLICY IF EXISTS enrollments_rls ON enrollments")
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
    _STUDENT_ROW = f"""
        {_CENTER}
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
    for table in ("grades", "exam_results", "attendance_records"):
        _replace_policy(table, f"{table}_rls", _STUDENT_ROW)
