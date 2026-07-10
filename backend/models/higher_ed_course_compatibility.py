"""Higher education course / secondary track compatibility ORM entity."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .higher_ed_course import HigherEdCourse
from .secondary_track import SecondaryTrack


class HigherEdCourseCompatibility(Base):
    __tablename__ = "higher_ed_course_compatibility"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("higher_ed_course.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    secondary_track_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("secondary_track.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    compatible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    course: Mapped[HigherEdCourse] = relationship(back_populates="compatibilities")
    track: Mapped[SecondaryTrack] = relationship(back_populates="course_compatibilities")
