"""Student session ORM entity.

This is a minimal anchor model so StudentInterest can establish a concrete
many-to-one relationship in the current repo slice.
"""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class StudentSession(Base):
    __tablename__ = "student_session"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    school_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    student_interests: Mapped[list["StudentInterest"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
