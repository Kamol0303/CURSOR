"""Add file_id to certificates for uploaded document storage.

Revision ID: 014_certificate_file
Revises: 013_center_onboarding
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "014_certificate_file"
down_revision: Union[str, None] = "013_center_onboarding"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "certificates",
        sa.Column("file_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("files.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("certificates", "file_id")
