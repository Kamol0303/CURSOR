"""Center profile onboarding flag.

Revision ID: 013_center_onboarding
Revises: 012_teacher_rls
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "013_center_onboarding"
down_revision: Union[str, None] = "012_teacher_rls"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "training_centers",
        sa.Column("profile_completed", sa.Boolean(), server_default="false", nullable=False),
    )
    op.execute("""
        UPDATE training_centers
        SET profile_completed = true
        WHERE stir IS NOT NULL
          AND phone IS NOT NULL
          AND address IS NOT NULL
          AND director_name IS NOT NULL
          AND deleted_at IS NULL
    """)


def downgrade() -> None:
    op.drop_column("training_centers", "profile_completed")
