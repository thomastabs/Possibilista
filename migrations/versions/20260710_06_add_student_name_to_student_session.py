"""Add student_name column to student_session.

Revision ID: 20260710_06
Revises: 20260710_05
Create Date: 2026-07-10 13:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260710_06"
down_revision = "20260710_05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "student_session",
        sa.Column("student_name", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("student_session", "student_name")
