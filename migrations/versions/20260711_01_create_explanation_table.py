"""Create explanation table.

Revision ID: 20260711_01
Revises: 20260710_09
Create Date: 2026-07-11 10:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260711_01"
down_revision = "20260710_09"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "explanation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("explanation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "facts",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
        sa.Column(
            "interpretations",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
        sa.Column(
            "unavailable_info",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.UniqueConstraint("explanation_id", name="uq_explanation_explanation_id"),
    )
    op.create_index(
        "ix_explanation_explanation_id",
        "explanation",
        ["explanation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_explanation_explanation_id", table_name="explanation")
    op.drop_table("explanation")
