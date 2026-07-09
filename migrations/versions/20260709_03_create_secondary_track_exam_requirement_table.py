"""Create secondary_track_exam_requirement table.

Revision ID: 20260709_03
Revises: 20260709_02
Create Date: 2026-07-09 13:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260709_03"
down_revision = "20260709_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "secondary_track_exam_requirement",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "track_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("secondary_track.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("exam_name", sa.String(length=255), nullable=False),
        sa.Column("timing", sa.String(length=255), nullable=False),
    )
    op.create_index(
        "ix_secondary_track_exam_requirement_track_id",
        "secondary_track_exam_requirement",
        ["track_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_secondary_track_exam_requirement_track_id",
        table_name="secondary_track_exam_requirement",
    )
    op.drop_table("secondary_track_exam_requirement")
