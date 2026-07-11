"""Document indexing endpoints (Stories 9389382, 9389384).

``auth: role:admin`` in the technical spec is not backed by a real role/permission system in
this repo slice (none exists yet for any endpoint) — enforced here as plain bearer-token
presence, same as every other endpoint. See ``DETERMINISTIC_STUBS.md``.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.profiling import get_db_session
from backend.services.document_ingestion_service import ingest_legal_framework_documents
from backend.services.indexing_status_service import get_indexing_status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
bearer_scheme = HTTPBearer(auto_error=True)

INDEXING_SUCCESS_MESSAGE_TEMPLATE = "Indexed {count} legal framework document(s)."
INDEXING_FAILURE_MESSAGE_TEMPLATE = (
    "Indexed {indexed_count} legal framework document(s); {error_count} document(s) were "
    "corrupted and excluded: {errors}"
)
INDEXING_UNEXPECTED_FAILURE_MESSAGE = "Unable to index legal framework documents."


class DocumentIndexingResponse(BaseModel):
    status: str
    message: str


class DocumentIndexingStatusResponse(BaseModel):
    legal_framework_status: str
    exam_guide_status: str
    secondary_track_definitions_status: str
    higher_ed_requirements_status: str
    errors: list[str]


@router.post("/index-legal-framework", response_model=DocumentIndexingResponse)
async def post_index_legal_framework(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentIndexingResponse:
    logger.info(
        "Received legal framework document indexing request.",
        extra={"scheme": credentials.scheme},
    )

    try:
        result = await ingest_legal_framework_documents(db)
    except Exception:
        logger.exception("Legal framework document indexing failed unexpectedly.")
        return DocumentIndexingResponse(
            status="failed", message=INDEXING_UNEXPECTED_FAILURE_MESSAGE
        )

    indexed_count = result["indexed_count"]
    errors = result["errors"]

    if errors:
        status_value = "failed"
        message = INDEXING_FAILURE_MESSAGE_TEMPLATE.format(
            indexed_count=indexed_count,
            error_count=len(errors),
            errors="; ".join(errors),
        )
    else:
        status_value = "success"
        message = INDEXING_SUCCESS_MESSAGE_TEMPLATE.format(count=indexed_count)

    logger.info(
        "Legal framework document indexing request completed.",
        extra={
            "status": status_value,
            "indexed_count": indexed_count,
            "errors_count": len(errors),
        },
    )

    return DocumentIndexingResponse(status=status_value, message=message)


@router.get("/indexing-status", response_model=DocumentIndexingStatusResponse)
async def get_documents_indexing_status(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentIndexingStatusResponse:
    logger.info(
        "Received document indexing status request.",
        extra={"scheme": credentials.scheme},
    )

    result = await get_indexing_status(db)

    logger.info(
        "Document indexing status prepared.",
        extra={
            "legal_framework_status": result["legal_framework_status"],
            "exam_guide_status": result["exam_guide_status"],
            "secondary_track_definitions_status": result["secondary_track_definitions_status"],
            "higher_ed_requirements_status": result["higher_ed_requirements_status"],
            "errors_count": len(result["errors"]),
        },
    )

    return DocumentIndexingStatusResponse(**result)
