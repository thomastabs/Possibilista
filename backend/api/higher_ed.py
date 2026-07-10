"""Higher education course compatibility endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.api.profiling import get_db_session
from backend.services.higher_ed_service import get_compatible_higher_ed_courses

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/higher-ed", tags=["higher-ed"])


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
        result = await get_compatible_higher_ed_courses(db, secondary_track_id)
    except SQLAlchemyError as exc:
        logger.exception("Failed to load compatible higher-ed courses.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load compatible higher education courses.",
        ) from exc

    return HigherEdCoursesResponse(
        courses=[HigherEdCourseOut(**course) for course in result["courses"]],
        message=result["message"],
    )
