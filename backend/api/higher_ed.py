"""Higher education course compatibility endpoints."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.api.profiling import get_db_session
from backend.models.higher_ed_course import HigherEdCourse
from backend.models.higher_ed_course_entrance_exam import HigherEdCourseEntranceExam
from backend.services.higher_ed_service import get_compatible_higher_ed_courses

ENTRANCE_EXAMS_UNAVAILABLE_MESSAGE = (
    "Exam requirements are unavailable for the selected course."
)

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
        parsed_course_id = UUID(course_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="course_id must be a valid UUID.",
        ) from exc

    try:
        course = await db.get(HigherEdCourse, parsed_course_id)
    except SQLAlchemyError as exc:
        logger.exception("Failed to load higher-ed course.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load higher education course.",
        ) from exc

    if course is None:
        return HigherEdCourseEntranceExamsResponse(
            available=False,
            exams=[],
            message=ENTRANCE_EXAMS_UNAVAILABLE_MESSAGE,
        )

    try:
        result = await db.execute(
            select(HigherEdCourseEntranceExam).where(
                HigherEdCourseEntranceExam.course_id == parsed_course_id
            )
        )
        exams = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Failed to load entrance exams.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load entrance exams.",
        ) from exc

    return HigherEdCourseEntranceExamsResponse(
        available=True,
        exams=[EntranceExamOut(name=exam.exam_name, weight=exam.weight) for exam in exams],
        message="",
    )
