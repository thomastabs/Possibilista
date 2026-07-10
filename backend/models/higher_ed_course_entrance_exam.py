"""Higher education course entrance exam ORM entity."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .higher_ed_course import HigherEdCourse


class HigherEdCourseEntranceExam(Base):
    __tablename__ = "higher_ed_course_entrance_exam"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("higher_ed_course.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exam_name: Mapped[str] = mapped_column(String(255), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)

    course: Mapped[HigherEdCourse] = relationship(back_populates="entrance_exams")
