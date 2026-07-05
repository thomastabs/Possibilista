"""Natural language question guidance endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from backend.services.natural_language_question import answer_natural_language_question

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
bearer_scheme = HTTPBearer(auto_error=True)


class NaturalLanguageQuestionRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str = Field(min_length=1)


class NaturalLanguageQuestionResponse(BaseModel):
    answer: str
    clarification_needed: bool
    clarification_options: list[str]
    out_of_scope: bool
    suggestion: str
    session_id: str


@router.post("/natural-language-question", response_model=NaturalLanguageQuestionResponse)
async def post_natural_language_question(
    payload: NaturalLanguageQuestionRequest,
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
):
    logger.info(
        "Received natural language question request.",
        extra={
            "session_id": payload.session_id,
            "scheme": credentials.scheme,
        },
    )

    try:
        return await answer_natural_language_question(payload.question, payload.session_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
