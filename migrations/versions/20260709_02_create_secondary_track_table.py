"""Create secondary_track and secondary_track_discipline tables.

Revision ID: 20260709_02
Revises: 20260709_01
Create Date: 2026-07-09 12:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260709_02"
down_revision = "20260709_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "secondary_track",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint("name", name="uq_secondary_track_name"),
    )

    op.create_table(
        "secondary_track_discipline",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "track_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("secondary_track.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("discipline_name", sa.String(length=255), nullable=False),
    )
    op.create_index(
        "ix_secondary_track_discipline_track_id",
        "secondary_track_discipline",
        ["track_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_secondary_track_discipline_track_id", table_name="secondary_track_discipline")
    op.drop_table("secondary_track_discipline")
    op.drop_table("secondary_track")
