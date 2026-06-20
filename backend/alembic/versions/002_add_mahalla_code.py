"""Add mahallas.code column

Revision ID: 002_mahalla_code
Revises: 001_initial
Create Date: 2026-06-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_mahalla_code"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("mahallas")}
    if "code" not in columns:
        op.add_column("mahallas", sa.Column("code", sa.String(20), nullable=True))
        op.execute("UPDATE mahallas SET code = 'MAH-' || substr(hex(id), 1, 8) WHERE code IS NULL")
        with op.batch_alter_table("mahallas") as batch_op:
            batch_op.alter_column("code", nullable=False)
        op.create_index("ix_mahallas_code", "mahallas", ["code"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("mahallas")}
    if "code" in columns:
        op.drop_index("ix_mahallas_code", table_name="mahallas")
        op.drop_column("mahallas", "code")
