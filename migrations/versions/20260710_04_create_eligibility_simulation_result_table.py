"""Create eligibility_simulation_result table.

Revision ID: 20260710_04
Revises: 20260710_03
Create Date: 2026-07-10 11:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260710_04"
down_revision = "20260710_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "eligibility_simulation_result",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "secondary_track_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("secondary_track.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "eligible_courses",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "incomplete_data", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column("message", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_eligibility_simulation_result_secondary_track_id",
        "eligibility_simulation_result",
        ["secondary_track_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_eligibility_simulation_result_secondary_track_id",
        table_name="eligibility_simulation_result",
    )
    op.drop_table("eligibility_simulation_result")
