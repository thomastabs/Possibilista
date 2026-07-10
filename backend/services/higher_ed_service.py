"""Higher education course compatibility retrieval service."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.higher_ed_course import HigherEdCourse
from backend.models.higher_ed_course_compatibility import HigherEdCourseCompatibility
from backend.models.secondary_track import SecondaryTrack

logger = logging.getLogger(__name__)

NO_DATA_MESSAGE = "No data is available for the entered secondary track."


async def get_compatible_higher_ed_courses(db: AsyncSession, secondary_track_id: str) -> dict[str, Any]:
    try:
        parsed_track_id = UUID(secondary_track_id)
    except (ValueError, AttributeError, TypeError):
        logger.info(
            "Rejected malformed secondary track id.",
            extra={"secondary_track_id": secondary_track_id},
        )
        return {"courses": [], "message": NO_DATA_MESSAGE}

    try:
        track = await db.get(SecondaryTrack, parsed_track_id)
    except SQLAlchemyError:
        logger.exception(
            "Failed to load secondary track.", extra={"secondary_track_id": secondary_track_id}
        )
        raise

    if track is None:
        logger.info(
            "Secondary track not found.", extra={"secondary_track_id": secondary_track_id}
        )
        return {"courses": [], "message": NO_DATA_MESSAGE}

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
    except SQLAlchemyError:
        logger.exception(
            "Failed to load compatible higher-ed courses.",
            extra={"secondary_track_id": secondary_track_id},
        )
        raise

    if not courses:
        logger.info(
            "No compatible higher-ed courses found for track.",
            extra={"secondary_track_id": secondary_track_id},
        )
        return {"courses": [], "message": NO_DATA_MESSAGE}

    logger.info(
        "Retrieved compatible higher-ed courses.",
        extra={"secondary_track_id": secondary_track_id, "course_count": len(courses)},
    )
    return {
        "courses": [{"id": str(course.id), "name": course.name} for course in courses],
        "message": "",
    }
