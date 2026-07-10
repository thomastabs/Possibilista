"""Add age column to student_session.

Revision ID: 20260710_07
Revises: 20260710_06
Create Date: 2026-07-10 14:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260710_07"
down_revision = "20260710_06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "student_session",
        sa.Column("age", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("student_session", "age")
