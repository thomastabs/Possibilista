"""Create higher_ed_course_compatibility table.

Revision ID: 20260710_02
Revises: 20260710_01
Create Date: 2026-07-10 09:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260710_02"
down_revision = "20260710_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "higher_ed_course_compatibility",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("higher_ed_course.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "secondary_track_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("secondary_track.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("compatible", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("message", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_higher_ed_course_compatibility_course_id",
        "higher_ed_course_compatibility",
        ["course_id"],
    )
    op.create_index(
        "ix_higher_ed_course_compatibility_secondary_track_id",
        "higher_ed_course_compatibility",
        ["secondary_track_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_higher_ed_course_compatibility_secondary_track_id",
        table_name="higher_ed_course_compatibility",
    )
    op.drop_index(
        "ix_higher_ed_course_compatibility_course_id",
        table_name="higher_ed_course_compatibility",
    )
    op.drop_table("higher_ed_course_compatibility")
