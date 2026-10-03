"""drop email_verification_tokens

Revision ID: b4d7c9e1a8f2
Revises: 8a1c4e2f9b70
Create Date: 2026-09-27 18:45:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "b4d7c9e1a8f2"
down_revision: Union[str, Sequence[str], None] = "8a1c4e2f9b70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS email_verification_tokens CASCADE")


def downgrade() -> None:
    pass
