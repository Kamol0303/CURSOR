"""Analytics read-only role grants (post-schema)

Revision ID: 006_analytics_grants
Revises: 005_phase4
"""

from typing import Sequence, Union

from alembic import op

revision: str = "006_analytics_grants"
down_revision: Union[str, None] = "005_phase4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'tamor_analytics') THEN
                CREATE ROLE tamor_analytics WITH LOGIN PASSWORD 'tamor_dev';
            END IF;
        END
        $$;
    """)
    op.execute("GRANT CONNECT ON DATABASE tamor TO tamor_analytics")
    op.execute("GRANT USAGE ON SCHEMA public TO tamor_analytics")
    op.execute("""
        GRANT SELECT ON training_centers, teachers, subjects, teacher_subjects,
            enrollments, groups, rating_history, rating_formula_versions,
            certificates TO tamor_analytics
    """)
    op.execute("GRANT SELECT, INSERT ON ai_predictions, ai_analysis_logs TO tamor_analytics")
    op.execute("REVOKE ALL ON students FROM tamor_analytics")
    op.execute("""
        GRANT SELECT (id, center_id, full_name, date_of_birth, grade, school, graduation_date,
            consent_given_at, is_demo_data, created_at, updated_at, deleted_at) ON students TO tamor_analytics
    """)


def downgrade() -> None:
    op.execute("REVOKE ALL ON students FROM tamor_analytics")
    op.execute("REVOKE ALL ON ai_predictions, ai_analysis_logs FROM tamor_analytics")
    op.execute("""
        REVOKE ALL ON training_centers, teachers, subjects, teacher_subjects,
            enrollments, groups, rating_history, rating_formula_versions,
            certificates FROM tamor_analytics
    """)
    op.execute("REVOKE USAGE ON SCHEMA public FROM tamor_analytics")
    op.execute("REVOKE CONNECT ON DATABASE tamor FROM tamor_analytics")
