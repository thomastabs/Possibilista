"""Add is_fact and is_interpretation flags to chat_message.

Revision ID: 20260710_09
Revises: 20260710_08
Create Date: 2026-07-11 09:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260710_09"
down_revision = "20260710_08"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chat_message",
        sa.Column("is_fact", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "chat_message",
        sa.Column("is_interpretation", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("chat_message", "is_interpretation")
    op.drop_column("chat_message", "is_fact")
