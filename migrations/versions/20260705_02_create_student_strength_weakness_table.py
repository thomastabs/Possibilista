"""Create student_strength_weakness table.

Revision ID: 20260705_02
Revises: 20260705_01
Create Date: 2026-07-05 12:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260705_02"
down_revision = "20260705_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_strength_weakness",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("student_session.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("strengths", sa.ARRAY(sa.Text()), nullable=False, server_default=sa.text("'{}'::text[]")),
        sa.Column("weaknesses", sa.ARRAY(sa.Text()), nullable=False, server_default=sa.text("'{}'::text[]")),
        sa.Column("partial", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index(
        "ix_student_strength_weakness_session_id",
        "student_strength_weakness",
        ["session_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_student_strength_weakness_session_id", table_name="student_strength_weakness")
    op.drop_table("student_strength_weakness")

