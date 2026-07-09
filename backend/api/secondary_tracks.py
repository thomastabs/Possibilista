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
