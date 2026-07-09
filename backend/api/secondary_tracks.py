"""Secondary education track listing endpoint."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.profiling import get_db_session
from backend.models.secondary_track import SecondaryTrack
from backend.services.secondary_track_service import (
    get_discipline_combinations_for_track,
    get_disciplines_for_track,
    get_exam_requirements_for_track,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/secondary-tracks", tags=["secondary-tracks"])


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
        result = await get_exam_requirements_for_track(db, track_id)
    except SQLAlchemyError as exc:
        logger.exception("Failed to load secondary track exam requirements.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load secondary track exam requirements.",
        ) from exc

    return SecondaryTrackExamRequirementsResponse(
        valid=result["valid"],
        exams=[
            ExamRequirementOut(name=exam["exam_name"], timing=exam["timing"])
            for exam in result["exams"]
        ],
        message=result["message"],
    )


class SecondaryTrackDisciplineCombinationsResponse(BaseModel):
    valid: bool
    trienais: list[str]
    bienais: list[str]
    anuais: list[str]
    combinations: list[str]
    message: str


@router.get(
    "/{track_id}/discipline-combinations",
    response_model=SecondaryTrackDisciplineCombinationsResponse,
)
async def get_secondary_track_discipline_combinations(
    track_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> SecondaryTrackDisciplineCombinationsResponse:
    logger.info(
        "Received secondary track discipline combinations request.", extra={"track_id": track_id}
    )

    try:
        result = await get_discipline_combinations_for_track(db, track_id)
    except SQLAlchemyError as exc:
        logger.exception("Failed to load secondary track discipline combinations.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load secondary track discipline combinations.",
        ) from exc

    return SecondaryTrackDisciplineCombinationsResponse(**result)
