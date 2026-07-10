"""Create higher_ed_course table.

Revision ID: 20260710_01
Revises: 20260709_05
Create Date: 2026-07-10 09:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260710_01"
down_revision = "20260709_05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "higher_ed_course",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.UniqueConstraint("name", name="uq_higher_ed_course_name"),
    )


def downgrade() -> None:
    op.drop_table("higher_ed_course")
