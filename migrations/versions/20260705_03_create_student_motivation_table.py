"""Create student_motivation table.

Revision ID: 20260705_03
Revises: 20260705_02
Create Date: 2026-07-05 13:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260705_03"
down_revision = "20260705_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_motivation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("student_session.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("motivations", sa.Text(), nullable=True),
        sa.Column("declined", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index(
        "ix_student_motivation_session_id",
        "student_motivation",
        ["session_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_student_motivation_session_id", table_name="student_motivation")
    op.drop_table("student_motivation")

