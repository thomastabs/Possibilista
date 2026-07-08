"""Create chat_message table with facts/interpretations breakdown.

Revision ID: 20260707_01
Revises: 20260705_03
Create Date: 2026-07-07 09:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260707_01"
down_revision = "20260705_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_message",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("student_session.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("facts", sa.ARRAY(sa.Text()), nullable=False, server_default=sa.text("'{}'::text[]")),
        sa.Column(
            "interpretations",
            sa.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
        sa.Column("insufficient_info", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("requires_confirmation", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_chat_message_session_id",
        "chat_message",
        ["session_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_chat_message_session_id", table_name="chat_message")
    op.drop_table("chat_message")
