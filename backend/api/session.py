"""Student session name endpoint."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.chat import resolve_student_session
from backend.api.profiling import get_db_session
from backend.services.session_service import record_student_interests, validate_school_year

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/session", tags=["session"])
bearer_scheme = HTTPBearer(auto_error=True)


class SessionNameRequest(BaseModel):
    session_id: str = Field(min_length=1)
    name: str | None = None
    skipped: bool = False


class SessionNameResponse(BaseModel):
    status: str
    message: str


SCHOOL_YEAR_SUCCESS_MESSAGE = "School year accepted."


class SchoolYearRequest(BaseModel):
    session_id: str = Field(min_length=1)
    school_year: int


class SchoolYearResponse(BaseModel):
    valid: bool
    message: str


MIN_AGE = 9
MAX_AGE = 12

AGE_SUCCESS_MESSAGE = "Age accepted."
AGE_INVALID_MESSAGE = f"Please provide a valid age between {MIN_AGE} and {MAX_AGE}."


class SessionAgeRequest(BaseModel):
    session_id: str = Field(min_length=1)
    age: int


class SessionAgeResponse(BaseModel):
    valid: bool
    message: str


class SessionInterestsRequest(BaseModel):
    interests: list[str] = Field(default_factory=list)
    skipped: bool = False
    session_id: str = Field(min_length=1)


class SessionInterestsResponse(BaseModel):
    status: str
    message: str


@router.post("/name", response_model=SessionNameResponse)
async def post_session_name(
    payload: SessionNameRequest,
    _credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> SessionNameResponse:
    student_session = await resolve_student_session(db, payload.session_id)

    if payload.skipped:
        student_name = None
        message = "Continuing without personalization."
    else:
        trimmed_name = (payload.name or "").strip()
        if not trimmed_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="name is required unless skipped is true.",
            )
        student_name = trimmed_name
        message = f"Thanks, {trimmed_name}! We'll use your name for this session."

    logger.info(
        "Updating student session name.",
        extra={"session_id": str(student_session.id), "skipped": payload.skipped},
    )

    student_session.student_name = student_name

    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Failed to persist student session name.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the student's name.",
        ) from exc

    return SessionNameResponse(status="success", message=message)


@router.post("/school-year", response_model=SchoolYearResponse)
async def post_school_year(
    payload: SchoolYearRequest,
    _credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> SchoolYearResponse:
    student_session = await resolve_student_session(db, payload.session_id)

    logger.info(
        "Received school year input.",
        extra={"session_id": str(student_session.id), "school_year": payload.school_year},
    )

    is_valid, invalid_message = validate_school_year(payload.school_year)
    if not is_valid:
        logger.info(
            "Rejected school year outside allowed range.",
            extra={"session_id": str(student_session.id), "school_year": payload.school_year},
        )
        return SchoolYearResponse(valid=False, message=invalid_message)

    student_session.school_year = payload.school_year

    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Failed to persist student session school year.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the student's school year.",
        ) from exc

    return SchoolYearResponse(valid=True, message=SCHOOL_YEAR_SUCCESS_MESSAGE)


@router.post("/age", response_model=SessionAgeResponse)
async def post_session_age(
    payload: SessionAgeRequest,
    _credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> SessionAgeResponse:
    student_session = await resolve_student_session(db, payload.session_id)

    logger.info(
        "Received age input.",
        extra={"session_id": str(student_session.id), "age": payload.age},
    )

    if not (MIN_AGE <= payload.age <= MAX_AGE):
        logger.info(
            "Rejected age outside allowed range.",
            extra={"session_id": str(student_session.id), "age": payload.age},
        )
        return SessionAgeResponse(valid=False, message=AGE_INVALID_MESSAGE)

    student_session.age = payload.age

    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Failed to persist student session age.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the student's age.",
        ) from exc

    return SessionAgeResponse(valid=True, message=AGE_SUCCESS_MESSAGE)


@router.post("/interests", response_model=SessionInterestsResponse)
async def post_session_interests(
    payload: SessionInterestsRequest,
    _credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> SessionInterestsResponse:
    student_session = await resolve_student_session(db, payload.session_id)

    logger.info(
        "Received interests input.",
        extra={"session_id": str(student_session.id), "skipped": payload.skipped},
    )

    saved_count = await record_student_interests(
        db, student_session, payload.interests, payload.skipped
    )

    message = (
        "Interests saved to tailor exploration."
        if saved_count > 0
        else "Continuing with general guidance."
    )

    return SessionInterestsResponse(status="success", message=message)
