"""Create session_secondary_track_memory table.

Revision ID: 20260710_08
Revises: 20260710_07
Create Date: 2026-07-10 15:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260710_08"
down_revision = "20260710_07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "session_secondary_track_memory",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("student_session.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "stored_track_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("secondary_track.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint("session_id", name="uq_session_secondary_track_memory_session_id"),
    )
    op.create_index(
        "ix_session_secondary_track_memory_session_id",
        "session_secondary_track_memory",
        ["session_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_session_secondary_track_memory_session_id",
        table_name="session_secondary_track_memory",
    )
    op.drop_table("session_secondary_track_memory")
