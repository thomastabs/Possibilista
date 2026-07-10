"""Create higher_ed_course_admission_average table.

Revision ID: 20260710_05
Revises: 20260710_04
Create Date: 2026-07-10 12:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260710_05"
down_revision = "20260710_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "higher_ed_course_admission_average",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("higher_ed_course.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("admission_average", sa.Float(), nullable=True),
        sa.Column("exam_weights", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.UniqueConstraint("course_id", name="uq_higher_ed_course_admission_average_course_id"),
    )
    op.create_index(
        "ix_higher_ed_course_admission_average_course_id",
        "higher_ed_course_admission_average",
        ["course_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_higher_ed_course_admission_average_course_id",
        table_name="higher_ed_course_admission_average",
    )
    op.drop_table("higher_ed_course_admission_average")
