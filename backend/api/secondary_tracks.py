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
from backend.models.secondary_track import SecondaryTrack, SecondaryTrackDiscipline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/secondary-tracks", tags=["secondary-tracks"])

UNKNOWN_TRACK_MESSAGE = (
    "That secondary track is not recognized. Please ask about one of the valid secondary tracks."
)


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
    try:
        parsed_track_id = UUID(track_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="track_id must be a valid UUID.",
        ) from exc

    try:
        track = await db.get(SecondaryTrack, parsed_track_id)
    except SQLAlchemyError as exc:
        logger.exception("Failed to load secondary track.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load secondary track.",
        ) from exc

    if track is None:
        return SecondaryTrackDisciplinesResponse(
            valid=False,
            disciplines=[],
            message=UNKNOWN_TRACK_MESSAGE,
        )

    try:
        result = await db.execute(
            select(SecondaryTrackDiscipline).where(SecondaryTrackDiscipline.track_id == parsed_track_id)
        )
        disciplines = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Failed to load secondary track disciplines.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load secondary track disciplines.",
        ) from exc

    return SecondaryTrackDisciplinesResponse(
        valid=True,
        disciplines=[discipline.discipline_name for discipline in disciplines],
        message="",
    )
