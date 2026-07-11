"""Institutional confirmation alert ORM entity — flags a student session's academic path as
needing institutional confirmation, and carries the family-facing alert message (Story 9389399)."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .student_session import StudentSession


class InstitutionalConfirmationAlert(Base):
    __tablename__ = "institutional_confirmation_alert"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("student_session.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    alert_present: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    alert_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    session: Mapped[StudentSession] = relationship(back_populates="institutional_confirmation_alert")
