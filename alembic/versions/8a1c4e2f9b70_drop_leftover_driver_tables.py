"""drop leftover driver tables

Revision ID: 8a1c4e2f9b70
Revises: ed3f40833632
Create Date: 2026-09-27 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "8a1c4e2f9b70"
down_revision: Union[str, Sequence[str], None] = "ed3f40833632"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS vehicles CASCADE")
    op.execute("DROP TABLE IF EXISTS fuel_profiles CASCADE")
    op.execute("DROP TABLE IF EXISTS drivers CASCADE")


def downgrade() -> None:
    pass
