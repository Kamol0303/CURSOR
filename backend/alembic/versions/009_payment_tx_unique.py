"""Unique external payment id for replay protection.

Revision ID: 009_payment_tx_unique
Revises: 008_ocms
"""

from typing import Sequence, Union

from alembic import op

revision: str = "009_payment_tx_unique"
down_revision: Union[str, None] = "008_ocms"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_payment_tx_provider_external
        ON payment_transactions (provider, external_id)
        WHERE external_id IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_payment_tx_provider_external")
