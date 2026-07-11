"""Indexing status aggregation across document types (Stories 9389382/84/86/88).

Backs ``GET /api/v1/documents/indexing-status``. A document type's status is derived live
from the current ``Document`` rows rather than a separately persisted status record: a type
with no rows at all is ``missing`` (Story 9389384's "system identifies the missing document"
is a query-time determination, surfaced here rather than through a separate alerting channel
that doesn't exist in this repo slice — see ``DETERMINISTIC_STUBS.md``).
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.document import Document

logger = logging.getLogger(__name__)

LEGAL_FRAMEWORK_DOCUMENT_TYPE = "legal_framework"
EXAM_GUIDE_DOCUMENT_TYPE = "exam_guide"
SECONDARY_TRACK_DEFINITIONS_DOCUMENT_TYPE = "secondary_track_definitions"
HIGHER_ED_REQUIREMENTS_DOCUMENT_TYPE = "higher_ed_requirements"

_ALL_DOCUMENT_TYPES = (
    LEGAL_FRAMEWORK_DOCUMENT_TYPE,
    EXAM_GUIDE_DOCUMENT_TYPE,
    SECONDARY_TRACK_DEFINITIONS_DOCUMENT_TYPE,
    HIGHER_ED_REQUIREMENTS_DOCUMENT_TYPE,
)

STATUS_INDEXED = "indexed"
STATUS_FAILED = "failed"
STATUS_MISSING = "missing"

_MISSING_DOCUMENT_MESSAGE_TEMPLATE = "{document_type}: document is missing."
_FAILED_DOCUMENT_MESSAGE_TEMPLATE = "{document_type}: indexing failed."


def _status_for_document_type(
    documents: list[Document], document_type: str
) -> tuple[str, list[str]]:
    matching = [document for document in documents if document.document_type == document_type]

    if not matching:
        return STATUS_MISSING, [
            _MISSING_DOCUMENT_MESSAGE_TEMPLATE.format(document_type=document_type)
        ]

    errors = [error for document in matching for error in (document.indexing_errors or [])]

    if any(document.indexed for document in matching):
        return STATUS_INDEXED, errors

    return STATUS_FAILED, errors or [
        _FAILED_DOCUMENT_MESSAGE_TEMPLATE.format(document_type=document_type)
    ]


async def get_indexing_status(db: AsyncSession) -> dict[str, Any]:
    """Aggregate per-document-type indexing status and errors for the admin status screen."""

    try:
        result = await db.execute(select(Document))
        documents = list(result.scalars().all())
    except SQLAlchemyError:
        logger.exception("Failed to load documents for indexing status.")
        documents = []

    errors: list[str] = []
    statuses: dict[str, str] = {}

    for document_type in _ALL_DOCUMENT_TYPES:
        status_value, type_errors = _status_for_document_type(documents, document_type)
        statuses[document_type] = status_value
        errors.extend(type_errors)

    logger.info(
        "Computed document indexing status.",
        extra={"statuses": statuses, "errors_count": len(errors)},
    )

    return {
        "legal_framework_status": statuses[LEGAL_FRAMEWORK_DOCUMENT_TYPE],
        "exam_guide_status": statuses[EXAM_GUIDE_DOCUMENT_TYPE],
        "secondary_track_definitions_status": statuses[
            SECONDARY_TRACK_DEFINITIONS_DOCUMENT_TYPE
        ],
        "higher_ed_requirements_status": statuses[HIGHER_ED_REQUIREMENTS_DOCUMENT_TYPE],
        "errors": errors,
    }
