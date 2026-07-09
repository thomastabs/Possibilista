"""Create secondary_track_higher_ed_impact table.

Revision ID: 20260709_05
Revises: 20260709_04
Create Date: 2026-07-09 15:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260709_05"
down_revision = "20260709_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "secondary_track_higher_ed_impact",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "track_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("secondary_track.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("impact_description", sa.Text(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.UniqueConstraint("track_id", name="uq_secondary_track_higher_ed_impact_track_id"),
    )
    op.create_index(
        "ix_secondary_track_higher_ed_impact_track_id",
        "secondary_track_higher_ed_impact",
        ["track_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_secondary_track_higher_ed_impact_track_id",
        table_name="secondary_track_higher_ed_impact",
    )
    op.drop_table("secondary_track_higher_ed_impact")
