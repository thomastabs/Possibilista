"""Create document table with pgvector embedding column.

Revision ID: 20260711_03
Revises: 20260711_02
Create Date: 2026-07-11 12:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql


revision = "20260711_03"
down_revision = "20260711_02"
branch_labels = None
depends_on = None

EMBEDDING_DIMENSIONS = 8


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "document",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_url", sa.String(512), nullable=False),
        sa.Column("document_type", sa.String(100), nullable=False),
        sa.Column("version_label", sa.String(100), nullable=False),
        sa.Column(
            "indexed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "indexing_errors",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
        sa.Column("embedding", Vector(EMBEDDING_DIMENSIONS), nullable=True),
        sa.UniqueConstraint("source_url", name="uq_document_source_url"),
    )
    op.create_index("ix_document_source_url", "document", ["source_url"])


def downgrade() -> None:
    op.drop_index("ix_document_source_url", table_name="document")
    op.drop_table("document")
