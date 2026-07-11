"""Family-focused explanation mode endpoints."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.profiling import get_db_session
from backend.models.student_session import StudentSession
from backend.services.family_service import get_exploration_path_explanation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/family", tags=["family"])
bearer_scheme = HTTPBearer(auto_error=True)

STUDENT_SESSION_NOT_FOUND_MESSAGE = "Student session not found."


class ExplorationPathResponse(BaseModel):
    interests_explanation: str
    motivations_explanation: str
    academic_areas_explanation: str
    no_data: bool


async def _resolve_family_student_session(
    db: AsyncSession, student_session_id: str
) -> StudentSession:
    try:
        session_uuid = UUID(student_session_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=STUDENT_SESSION_NOT_FOUND_MESSAGE,
        ) from exc

    result = await db.execute(select(StudentSession).where(StudentSession.id == session_uuid))
    student_session = result.scalar_one_or_none()
    if student_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=STUDENT_SESSION_NOT_FOUND_MESSAGE,
        )
    return student_session


@router.get("/exploration-path", response_model=ExplorationPathResponse)
async def get_exploration_path(
    student_session_id: str = Query(min_length=1),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> ExplorationPathResponse:
    logger.info(
        "Received exploration path explanation request.",
        extra={"student_session_id": student_session_id, "scheme": credentials.scheme},
    )

    student_session = await _resolve_family_student_session(db, student_session_id)

    result = await get_exploration_path_explanation(db, str(student_session.id))

    logger.info(
        "Exploration path explanation prepared.",
        extra={"student_session_id": str(student_session.id), "no_data": result["no_data"]},
    )

    return ExplorationPathResponse(**result)
