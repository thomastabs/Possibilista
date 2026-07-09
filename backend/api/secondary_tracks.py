"""Secondary education track listing endpoint."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.profiling import get_db_session
from backend.models.secondary_track import SecondaryTrack, SecondaryTrackExamRequirement
from backend.services.secondary_track_service import get_disciplines_for_track

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/secondary-tracks", tags=["secondary-tracks"])

EXAM_REQUIREMENTS_INVALID_FORMAT_MESSAGE = "Invalid track ID format."
EXAM_REQUIREMENTS_UNKNOWN_TRACK_MESSAGE = (
    "No information is available for that track. Please ask about valid tracks."
)
EXAM_REQUIREMENTS_SUCCESS_MESSAGE = "Exam requirements retrieved successfully."


class SecondaryTrackOut(BaseModel):
    id: str
    name: str
    description: str | None = None


class SecondaryTracksResponse(BaseModel):
    tracks: list[SecondaryTrackOut]


@router.get("", response_model=SecondaryTracksResponse)
async def get_secondary_tracks(
    db: AsyncSession = Depends(get_db_session),
) -> SecondaryTracksResponse:
    try:
        result = await db.execute(select(SecondaryTrack))
        tracks = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Failed to load secondary tracks.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load secondary tracks.",
        ) from exc

    return SecondaryTracksResponse(
        tracks=[
            SecondaryTrackOut(id=str(track.id), name=track.name, description=track.description)
            for track in tracks
        ]
    )


class SecondaryTrackDisciplinesResponse(BaseModel):
    valid: bool
    disciplines: list[str]
    message: str


@router.get("/{track_id}/disciplines", response_model=SecondaryTrackDisciplinesResponse)
async def get_secondary_track_disciplines(
    track_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> SecondaryTrackDisciplinesResponse:
    logger.info("Received secondary track disciplines request.", extra={"track_id": track_id})

    try:
        result = await get_disciplines_for_track(db, track_id)
    except SQLAlchemyError as exc:
        logger.exception("Failed to load secondary track disciplines.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load secondary track disciplines.",
        ) from exc

    return SecondaryTrackDisciplinesResponse(**result)


class ExamRequirementOut(BaseModel):
    name: str
    timing: str


class SecondaryTrackExamRequirementsResponse(BaseModel):
    valid: bool
    exams: list[ExamRequirementOut]
    message: str


@router.get("/{track_id}/exam-requirements", response_model=SecondaryTrackExamRequirementsResponse)
async def get_secondary_track_exam_requirements(
    track_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> SecondaryTrackExamRequirementsResponse:
    logger.info("Received secondary track exam requirements request.", extra={"track_id": track_id})

    try:
        parsed_track_id = UUID(track_id)
    except ValueError:
        logger.info("Rejected malformed secondary track id.", extra={"track_id": track_id})
        return SecondaryTrackExamRequirementsResponse(
            valid=False,
            exams=[],
            message=EXAM_REQUIREMENTS_INVALID_FORMAT_MESSAGE,
        )

    try:
        track = await db.get(SecondaryTrack, parsed_track_id)
    except SQLAlchemyError as exc:
        logger.exception("Failed to load secondary track.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load secondary track.",
        ) from exc

    if track is None:
        return SecondaryTrackExamRequirementsResponse(
            valid=False,
            exams=[],
            message=EXAM_REQUIREMENTS_UNKNOWN_TRACK_MESSAGE,
        )

    try:
        result = await db.execute(
            select(SecondaryTrackExamRequirement).where(
                SecondaryTrackExamRequirement.track_id == parsed_track_id
            )
        )
        exam_requirements = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Failed to load secondary track exam requirements.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load secondary track exam requirements.",
        ) from exc

    return SecondaryTrackExamRequirementsResponse(
        valid=True,
        exams=[
            ExamRequirementOut(name=exam.exam_name, timing=exam.timing)
            for exam in exam_requirements
        ],
        message=EXAM_REQUIREMENTS_SUCCESS_MESSAGE,
    )
