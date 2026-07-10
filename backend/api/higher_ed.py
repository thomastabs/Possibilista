"""Higher education course compatibility endpoints."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.api.profiling import get_db_session
from backend.models.secondary_track import SecondaryTrack
from backend.services.higher_ed_service import (
    get_admission_averages_for_course,
    get_compatibility_for_secondary_track,
    get_compatible_higher_ed_courses,
    get_entrance_exams_for_course,
    simulate_eligibility_for_secondary_track,
)

COMPATIBILITY_FEEDBACK_CORRECT_INPUT_MESSAGE = (
    "Please correct your secondary track input; the track was not recognized."
)
COMPATIBILITY_FEEDBACK_COMPLETE_INPUT_MESSAGE = (
    "Please complete your secondary track input; no compatibility data is available yet."
)
COMPATIBILITY_FEEDBACK_NO_COMPATIBLE_COURSES_MESSAGE = (
    "No compatible higher education courses were found for this secondary track."
)
COMPATIBILITY_FEEDBACK_SUCCESS_MESSAGE = (
    "Compatible higher education courses were found for this secondary track."
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/higher-ed", tags=["higher-ed"])
bearer_scheme = HTTPBearer(auto_error=True)


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


class EntranceExamOut(BaseModel):
    name: str
    weight: float


class HigherEdCourseEntranceExamsResponse(BaseModel):
    available: bool
    exams: list[EntranceExamOut]
    message: str


@router.get(
    "/courses/{course_id}/entrance-exams",
    response_model=HigherEdCourseEntranceExamsResponse,
)
async def get_higher_ed_course_entrance_exams(
    course_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> HigherEdCourseEntranceExamsResponse:
    logger.info("Received entrance exams request.", extra={"course_id": course_id})

    try:
        UUID(course_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="course_id must be a valid UUID.",
        ) from exc

    try:
        result = await get_entrance_exams_for_course(db, course_id)
    except SQLAlchemyError as exc:
        logger.exception("Failed to load entrance exams.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load entrance exams.",
        ) from exc

    return HigherEdCourseEntranceExamsResponse(
        available=result["available"],
        exams=[EntranceExamOut(**exam) for exam in result["exams"]],
        message=result["message"],
    )


class EligibilitySimulationRequest(BaseModel):
    secondary_track_id: str = Field(min_length=1)


class EligibilitySimulationResponse(BaseModel):
    eligible_courses: list[HigherEdCourseOut]
    incomplete_data: bool
    message: str


@router.post("/eligibility-simulation", response_model=EligibilitySimulationResponse)
async def post_eligibility_simulation(
    payload: EligibilitySimulationRequest,
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> EligibilitySimulationResponse:
    logger.info(
        "Received eligibility simulation request.",
        extra={"secondary_track_id": payload.secondary_track_id, "scheme": credentials.scheme},
    )

    try:
        UUID(payload.secondary_track_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="secondary_track_id must be a valid UUID.",
        ) from exc

    try:
        result = await simulate_eligibility_for_secondary_track(db, payload.secondary_track_id)
    except SQLAlchemyError as exc:
        logger.exception("Failed to simulate eligibility.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to simulate eligibility for the selected secondary track.",
        ) from exc

    return EligibilitySimulationResponse(
        eligible_courses=[HigherEdCourseOut(**course) for course in result["eligible_courses"]],
        incomplete_data=result["incomplete_data"],
        message=result["message"],
    )


class ExamWeightOut(BaseModel):
    exam_name: str
    weight: float


class HigherEdCourseAdmissionAveragesResponse(BaseModel):
    available: bool
    admission_average: float | None
    exam_weights: list[ExamWeightOut]
    message: str


@router.get(
    "/courses/{course_id}/admission-averages",
    response_model=HigherEdCourseAdmissionAveragesResponse,
)
async def get_higher_ed_course_admission_averages(
    course_id: str,
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> HigherEdCourseAdmissionAveragesResponse:
    logger.info(
        "Received admission averages request.",
        extra={"course_id": course_id, "scheme": credentials.scheme},
    )

    try:
        UUID(course_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="course_id must be a valid UUID.",
        ) from exc

    try:
        result = await get_admission_averages_for_course(db, course_id)
    except SQLAlchemyError as exc:
        logger.exception("Failed to load admission averages.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load admission averages.",
        ) from exc

    return HigherEdCourseAdmissionAveragesResponse(
        available=result["available"],
        admission_average=result["admission_average"],
        exam_weights=[ExamWeightOut(**weight) for weight in result["exam_weights"]],
        message=result["message"],
    )


class CompatibilityFeedbackRequest(BaseModel):
    secondary_track_id: str = Field(min_length=1)


class CompatibilityFeedbackResponse(BaseModel):
    compatible: bool
    message: str


@router.post("/compatibility-feedback", response_model=CompatibilityFeedbackResponse)
async def post_compatibility_feedback(
    payload: CompatibilityFeedbackRequest,
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> CompatibilityFeedbackResponse:
    logger.info(
        "Received compatibility feedback request.",
        extra={"secondary_track_id": payload.secondary_track_id, "scheme": credentials.scheme},
    )

    try:
        parsed_track_id = UUID(payload.secondary_track_id)
    except ValueError:
        logger.info(
            "Rejected malformed secondary track id.",
            extra={"secondary_track_id": payload.secondary_track_id},
        )
        return CompatibilityFeedbackResponse(
            compatible=False,
            message=COMPATIBILITY_FEEDBACK_CORRECT_INPUT_MESSAGE,
        )

    try:
        track = await db.get(SecondaryTrack, parsed_track_id)
    except SQLAlchemyError as exc:
        logger.exception("Failed to load secondary track.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load compatibility data for the selected secondary track.",
        ) from exc

    if track is None:
        logger.info(
            "Secondary track not found.",
            extra={"secondary_track_id": payload.secondary_track_id},
        )
        return CompatibilityFeedbackResponse(
            compatible=False,
            message=COMPATIBILITY_FEEDBACK_CORRECT_INPUT_MESSAGE,
        )

    try:
        compatibilities = await get_compatibility_for_secondary_track(
            db, payload.secondary_track_id
        )
    except SQLAlchemyError as exc:
        logger.exception("Failed to load compatibility data.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load compatibility data for the selected secondary track.",
        ) from exc

    if not compatibilities:
        logger.info(
            "No compatibility data found for secondary track.",
            extra={"secondary_track_id": payload.secondary_track_id},
        )
        return CompatibilityFeedbackResponse(
            compatible=False,
            message=COMPATIBILITY_FEEDBACK_COMPLETE_INPUT_MESSAGE,
        )

    if any(compatibility.compatible for compatibility in compatibilities):
        return CompatibilityFeedbackResponse(
            compatible=True,
            message=COMPATIBILITY_FEEDBACK_SUCCESS_MESSAGE,
        )

    return CompatibilityFeedbackResponse(
        compatible=False,
        message=COMPATIBILITY_FEEDBACK_NO_COMPATIBLE_COURSES_MESSAGE,
    )
