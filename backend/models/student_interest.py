"""Student interest ORM entity."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .student_session import StudentSession


class StudentInterest(Base):
    __tablename__ = "student_interest"

    __table_args__ = (
        CheckConstraint(
            "skipped OR interest IS NOT NULL",
            name="interest_required_when_not_skipped",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("student_session.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    interest: Mapped[str | None] = mapped_column(Text, nullable=True)
    skipped: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    session: Mapped[StudentSession] = relationship(back_populates="student_interests")
