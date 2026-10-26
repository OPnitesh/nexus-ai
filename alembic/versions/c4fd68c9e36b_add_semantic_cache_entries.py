
"""add semantic cache entries

Revision ID: c4fd68c9e36b
Revises: b4d7c9e1a8f2
Create Date: 2026-10-11 16:42:25.888526
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql


# Revision identifiers used by Alembic.
revision: str = "c4fd68c9e36b"
down_revision: Union[str, Sequence[str], None] = "b4d7c9e1a8f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Creates only the semantic-cache table and its index.
def upgrade() -> None:
    op.create_table(
        "semantic_cache_entries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(768), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("context_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_semantic_cache_entries_context_model",
        "semantic_cache_entries",
        ["context_hash", "model_name"],
        unique=False,
    )


# Removes only the semantic-cache table during rollback.
def downgrade() -> None:
    op.drop_index(
        "ix_semantic_cache_entries_context_model",
        table_name="semantic_cache_entries",
    )
    op.drop_table("semantic_cache_entries")
