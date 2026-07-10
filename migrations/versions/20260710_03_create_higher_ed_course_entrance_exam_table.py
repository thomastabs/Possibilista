"""Create higher_ed_course_entrance_exam table.

Revision ID: 20260710_03
Revises: 20260710_02
Create Date: 2026-07-10 10:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260710_03"
down_revision = "20260710_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "higher_ed_course_entrance_exam",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("higher_ed_course.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("exam_name", sa.String(length=255), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
    )
    op.create_index(
        "ix_higher_ed_course_entrance_exam_course_id",
        "higher_ed_course_entrance_exam",
        ["course_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_higher_ed_course_entrance_exam_course_id",
        table_name="higher_ed_course_entrance_exam",
    )
    op.drop_table("higher_ed_course_entrance_exam")
