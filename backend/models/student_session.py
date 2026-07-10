"""Student session ORM entity.

This is a minimal anchor model so profiling entities can establish concrete
many-to-one relationships in the current repo slice.
"""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class StudentSession(Base):
    __tablename__ = "student_session"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    school_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    student_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)

    student_interests: Mapped[list["StudentInterest"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    student_strength_weaknesses: Mapped[list["StudentStrengthWeakness"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    student_motivation: Mapped["StudentMotivation | None"] = relationship(
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    secondary_track_memory: Mapped["SessionSecondaryTrackMemory | None"] = relationship(
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )
