"""Higher education course admission average ORM entity."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .higher_ed_course import HigherEdCourse


class HigherEdCourseAdmissionAverage(Base):
    __tablename__ = "higher_ed_course_admission_average"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("higher_ed_course.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    admission_average: Mapped[float | None] = mapped_column(Float, nullable=True)
    exam_weights: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    course: Mapped[HigherEdCourse] = relationship(back_populates="admission_average")
