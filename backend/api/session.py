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


MIN_SCHOOL_YEAR = 9
MAX_SCHOOL_YEAR = 12

SCHOOL_YEAR_SUCCESS_MESSAGE = "School year accepted."
SCHOOL_YEAR_INVALID_MESSAGE = (
    f"Please provide a valid school year between {MIN_SCHOOL_YEAR} and {MAX_SCHOOL_YEAR}."
)


class SchoolYearRequest(BaseModel):
    session_id: str = Field(min_length=1)
    school_year: int


class SchoolYearResponse(BaseModel):
    valid: bool
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

    if not (MIN_SCHOOL_YEAR <= payload.school_year <= MAX_SCHOOL_YEAR):
        logger.info(
            "Rejected school year outside allowed range.",
            extra={"session_id": str(student_session.id), "school_year": payload.school_year},
        )
        return SchoolYearResponse(valid=False, message=SCHOOL_YEAR_INVALID_MESSAGE)

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
