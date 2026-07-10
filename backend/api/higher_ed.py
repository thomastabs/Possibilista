"""Higher education course compatibility endpoints."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.profiling import get_db_session
from backend.models.higher_ed_course import HigherEdCourse
from backend.models.higher_ed_course_compatibility import HigherEdCourseCompatibility

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/higher-ed", tags=["higher-ed"])

NO_DATA_MESSAGE = "No data is available for the entered secondary track."


class HigherEdCourseOut(BaseModel):
    id: str
    name: str


class HigherEdCoursesResponse(BaseModel):
    courses: list[HigherEdCourseOut]
    message: str


@router.get("/courses", response_model=HigherEdCoursesResponse)
async def get_higher_ed_courses(
    secondary_track_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> HigherEdCoursesResponse:
    logger.info(
        "Received higher-ed courses request.", extra={"secondary_track_id": secondary_track_id}
    )

    try:
        parsed_track_id = UUID(secondary_track_id)
    except ValueError:
        logger.info(
            "Rejected malformed secondary track id.",
            extra={"secondary_track_id": secondary_track_id},
        )
        return HigherEdCoursesResponse(courses=[], message=NO_DATA_MESSAGE)

    try:
        result = await db.execute(
            select(HigherEdCourse)
            .join(
                HigherEdCourseCompatibility,
                HigherEdCourseCompatibility.course_id == HigherEdCourse.id,
            )
            .where(
                HigherEdCourseCompatibility.secondary_track_id == parsed_track_id,
                HigherEdCourseCompatibility.compatible.is_(True),
            )
        )
        courses = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Failed to load compatible higher-ed courses.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load compatible higher education courses.",
        ) from exc

    if not courses:
        return HigherEdCoursesResponse(courses=[], message=NO_DATA_MESSAGE)

    return HigherEdCoursesResponse(
        courses=[HigherEdCourseOut(id=str(course.id), name=course.name) for course in courses],
        message="",
    )
