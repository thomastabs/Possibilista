"""Add no_basis flag to chat_message.

Revision ID: 20260711_04
Revises: 20260711_03
Create Date: 2026-07-11 13:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260711_04"
down_revision = "20260711_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chat_message",
        sa.Column("no_basis", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("chat_message", "no_basis")
