"""Escalation / confirmation-requirement notification endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from backend.services.chat_service import build_chat_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/escalation", tags=["escalation"])
bearer_scheme = HTTPBearer(auto_error=True)

CONFIRMATION_REQUIRED_MESSAGE = "This question requires human or institutional confirmation."
NO_CONFIRMATION_NEEDED_MESSAGE = "No confirmation needed."


class EscalationConfirmationNotificationResponse(BaseModel):
    requires_confirmation: bool
    message: str


@router.get(
    "/confirmation-notification",
    response_model=EscalationConfirmationNotificationResponse,
)
async def get_confirmation_notification(
    question: str = Query(min_length=1),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> EscalationConfirmationNotificationResponse:
    logger.info(
        "Received confirmation notification request.",
        extra={"question": question, "scheme": credentials.scheme},
    )

    result = build_chat_response(question, "escalation-confirmation-check")
    requires_confirmation = result["requires_confirmation"]

    logger.info(
        "Confirmation notification determined.",
        extra={"question": question, "requires_confirmation": requires_confirmation},
    )

    return EscalationConfirmationNotificationResponse(
        requires_confirmation=requires_confirmation,
        message=(
            CONFIRMATION_REQUIRED_MESSAGE
            if requires_confirmation
            else NO_CONFIRMATION_NEEDED_MESSAGE
        ),
    )
