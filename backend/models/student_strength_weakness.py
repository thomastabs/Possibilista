"""Student strength/weakness ORM entity."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .student_session import StudentSession


class StudentStrengthWeakness(Base):
    __tablename__ = "student_strength_weakness"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("student_session.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    strengths: Mapped[list[str]] = mapped_column(
        ARRAY(Text()),
        nullable=False,
        server_default=text("'{}'::text[]"),
    )
    weaknesses: Mapped[list[str]] = mapped_column(
        ARRAY(Text()),
        nullable=False,
        server_default=text("'{}'::text[]"),
    )
    partial: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    session: Mapped[StudentSession] = relationship(back_populates="student_strength_weaknesses")
