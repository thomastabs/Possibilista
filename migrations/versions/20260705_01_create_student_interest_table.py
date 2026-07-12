"""Create student_interest table.

Revision ID: 20260705_01
Revises:
Create Date: 2026-07-05 12:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260705_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_session",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("school_year", sa.Integer(), nullable=True),
    )

    op.create_table(
        "student_interest",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("student_session.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("interest", sa.Text(), nullable=True),
        sa.Column("skipped", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.CheckConstraint(
            "skipped OR interest IS NOT NULL",
            name="interest_required_when_not_skipped",
        ),
    )
    op.create_index(
        "ix_student_interest_session_id",
        "student_interest",
        ["session_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_student_interest_session_id", table_name="student_interest")
    op.drop_table("student_interest")
    op.drop_table("student_session")
