"""Create institutional_confirmation_alert table.

Revision ID: 20260711_02
Revises: 20260711_01
Create Date: 2026-07-11 11:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260711_02"
down_revision = "20260711_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "institutional_confirmation_alert",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("student_session.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "alert_present",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("alert_message", sa.Text(), nullable=True),
        sa.UniqueConstraint(
            "session_id", name="uq_institutional_confirmation_alert_session_id"
        ),
    )
    op.create_index(
        "ix_institutional_confirmation_alert_session_id",
        "institutional_confirmation_alert",
        ["session_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_institutional_confirmation_alert_session_id",
        table_name="institutional_confirmation_alert",
    )
    op.drop_table("institutional_confirmation_alert")
