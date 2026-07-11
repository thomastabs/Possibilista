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
from backend.services.family_service import (
    get_exploration_path_explanation,
    get_fact_interpretation_distinction,
    get_guidance_outcomes,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/family", tags=["family"])
bearer_scheme = HTTPBearer(auto_error=True)

STUDENT_SESSION_NOT_FOUND_MESSAGE = "Student session not found."
INVALID_EXPLANATION_ID_MESSAGE = "explanation_id must be a valid UUID."


class ExplorationPathResponse(BaseModel):
    interests_explanation: str
    motivations_explanation: str
    academic_areas_explanation: str
    no_data: bool


class FactInterpretationDistinctionResponse(BaseModel):
    facts: list[str]
    interpretations: list[str]
    unavailable_info: bool


class GuidanceRecommendation(BaseModel):
    text: str
    source: str


class GuidanceOutcomesResponse(BaseModel):
    recommendations: list[GuidanceRecommendation]
    pending: bool


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


@router.get(
    "/fact-interpretation-distinction",
    response_model=FactInterpretationDistinctionResponse,
)
async def get_fact_interpretation_distinction_endpoint(
    explanation_id: str = Query(min_length=1),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> FactInterpretationDistinctionResponse:
    try:
        UUID(explanation_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_EXPLANATION_ID_MESSAGE,
        ) from exc

    logger.info(
        "Received fact-interpretation distinction request.",
        extra={"explanation_id": explanation_id, "scheme": credentials.scheme},
    )

    result = await get_fact_interpretation_distinction(db, explanation_id)

    logger.info(
        "Fact-interpretation distinction prepared.",
        extra={"explanation_id": explanation_id, "unavailable_info": result["unavailable_info"]},
    )

    return FactInterpretationDistinctionResponse(**result)


@router.get("/guidance-outcomes", response_model=GuidanceOutcomesResponse)
async def get_guidance_outcomes_endpoint(
    student_session_id: str = Query(min_length=1),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> GuidanceOutcomesResponse:
    logger.info(
        "Received guidance outcomes request.",
        extra={"student_session_id": student_session_id, "scheme": credentials.scheme},
    )

    student_session = await _resolve_family_student_session(db, student_session_id)

    result = await get_guidance_outcomes(db, str(student_session.id))

    logger.info(
        "Guidance outcomes prepared.",
        extra={
            "student_session_id": str(student_session.id),
            "recommendations_count": len(result["recommendations"]),
            "pending": result["pending"],
        },
    )

    return GuidanceOutcomesResponse(**result)
