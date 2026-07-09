"""Secondary track discipline retrieval service."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.secondary_track import (
    SecondaryTrack,
    SecondaryTrackDiscipline,
    SecondaryTrackExamRequirement,
)

logger = logging.getLogger(__name__)

INVALID_FORMAT_MESSAGE = "Invalid track ID format."
TRACK_NOT_FOUND_MESSAGE = "The specified secondary track does not exist. Please ask about valid tracks."
SUCCESS_MESSAGE = "Disciplines retrieved successfully."

EXAM_REQUIREMENTS_INVALID_FORMAT_MESSAGE = "Invalid track ID format."
EXAM_REQUIREMENTS_UNKNOWN_TRACK_MESSAGE = (
    "No information is available for that track. Please ask about valid tracks."
)
EXAM_REQUIREMENTS_SUCCESS_MESSAGE = "Exam requirements retrieved successfully."


async def get_disciplines_for_track(db: AsyncSession, track_id: str) -> dict[str, Any]:
    try:
        parsed_track_id = UUID(track_id)
    except (ValueError, AttributeError, TypeError):
        logger.info("Rejected malformed secondary track id.", extra={"track_id": track_id})
        return {"valid": False, "disciplines": [], "message": INVALID_FORMAT_MESSAGE}

    try:
        track = await db.get(SecondaryTrack, parsed_track_id)
    except SQLAlchemyError:
        logger.exception("Failed to load secondary track.", extra={"track_id": track_id})
        raise

    if track is None:
        logger.info("Secondary track not found.", extra={"track_id": track_id})
        return {"valid": False, "disciplines": [], "message": TRACK_NOT_FOUND_MESSAGE}

    try:
        result = await db.execute(
            select(SecondaryTrackDiscipline).where(SecondaryTrackDiscipline.track_id == parsed_track_id)
        )
        disciplines = result.scalars().all()
    except SQLAlchemyError:
        logger.exception("Failed to load secondary track disciplines.", extra={"track_id": track_id})
        raise

    logger.info(
        "Retrieved secondary track disciplines.",
        extra={"track_id": track_id, "discipline_count": len(disciplines)},
    )
    return {
        "valid": True,
        "disciplines": [discipline.discipline_name for discipline in disciplines],
        "message": SUCCESS_MESSAGE,
    }


async def get_exam_requirements_for_track(db: AsyncSession, track_id: str) -> dict[str, Any]:
    try:
        parsed_track_id = UUID(track_id)
    except (ValueError, AttributeError, TypeError):
        logger.info("Rejected malformed secondary track id.", extra={"track_id": track_id})
        return {"valid": False, "exams": [], "message": EXAM_REQUIREMENTS_INVALID_FORMAT_MESSAGE}

    try:
        track = await db.get(SecondaryTrack, parsed_track_id)
    except SQLAlchemyError:
        logger.exception("Failed to load secondary track.", extra={"track_id": track_id})
        raise

    if track is None:
        logger.info("Secondary track not found.", extra={"track_id": track_id})
        return {"valid": False, "exams": [], "message": EXAM_REQUIREMENTS_UNKNOWN_TRACK_MESSAGE}

    try:
        result = await db.execute(
            select(SecondaryTrackExamRequirement).where(
                SecondaryTrackExamRequirement.track_id == parsed_track_id
            )
        )
        exam_requirements = result.scalars().all()
    except SQLAlchemyError:
        logger.exception(
            "Failed to load secondary track exam requirements.", extra={"track_id": track_id}
        )
        raise

    logger.info(
        "Retrieved secondary track exam requirements.",
        extra={"track_id": track_id, "exam_count": len(exam_requirements)},
    )
    return {
        "valid": True,
        "exams": [
            {"exam_name": exam.exam_name, "timing": exam.timing} for exam in exam_requirements
        ],
        "message": EXAM_REQUIREMENTS_SUCCESS_MESSAGE,
    }
