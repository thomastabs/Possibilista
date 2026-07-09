"""Create secondary_track_discipline_combination table.

Revision ID: 20260709_04
Revises: 20260709_03
Create Date: 2026-07-09 14:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260709_04"
down_revision = "20260709_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "secondary_track_discipline_combination",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "track_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("secondary_track.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("trienais", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("bienais", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("anuais", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("combinations", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("message", sa.Text(), nullable=True),
        sa.UniqueConstraint("track_id", name="uq_secondary_track_discipline_combination_track_id"),
    )
    op.create_index(
        "ix_secondary_track_discipline_combination_track_id",
        "secondary_track_discipline_combination",
        ["track_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_secondary_track_discipline_combination_track_id",
        table_name="secondary_track_discipline_combination",
    )
    op.drop_table("secondary_track_discipline_combination")
