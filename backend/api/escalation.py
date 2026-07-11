"""Escalation / confirmation-requirement notification endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from backend.services.chat_service import build_chat_response, detect_critical_decision, suggest_escalation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/escalation", tags=["escalation"])
bearer_scheme = HTTPBearer(auto_error=True)

CONFIRMATION_REQUIRED_MESSAGE = "This question requires human or institutional confirmation."
NO_CONFIRMATION_NEEDED_MESSAGE = "No confirmation needed."
NO_CRITICAL_DECISION_MESSAGE = "No critical decision detected."


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


class EscalationCriticalDecisionRoutingResponse(BaseModel):
    critical_decision_detected: bool
    suggestion: str


@router.get(
    "/critical-decision-routing",
    response_model=EscalationCriticalDecisionRoutingResponse,
)
async def get_critical_decision_routing(
    conversation_context: str = Query(min_length=1),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> EscalationCriticalDecisionRoutingResponse:
    logger.info(
        "Received critical decision routing request.",
        extra={"conversation_context": conversation_context, "scheme": credentials.scheme},
    )

    critical_decision_detected = detect_critical_decision(conversation_context)
    suggestion = (
        suggest_escalation(conversation_context)
        if critical_decision_detected
        else NO_CRITICAL_DECISION_MESSAGE
    )

    logger.info(
        "Critical decision routing determined.",
        extra={
            "conversation_context": conversation_context,
            "critical_decision_detected": critical_decision_detected,
        },
    )

    return EscalationCriticalDecisionRoutingResponse(
        critical_decision_detected=critical_decision_detected,
        suggestion=suggestion,
    )
