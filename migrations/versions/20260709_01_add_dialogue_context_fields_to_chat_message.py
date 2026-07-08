"""Add dialogue context fields to chat_message table.

Revision ID: 20260709_01
Revises: 20260707_01
Create Date: 2026-07-09 09:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260709_01"
down_revision = "20260707_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chat_message",
        sa.Column(
            "previous_message_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("chat_message.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "chat_message",
        sa.Column("context_tokens", sa.ARRAY(sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("chat_message", "context_tokens")
    op.drop_column("chat_message", "previous_message_id")
