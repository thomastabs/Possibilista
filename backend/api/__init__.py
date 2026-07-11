"""FastAPI routers for Possibilista."""

from fastapi import APIRouter

from backend.api.chat import answers_router, router as chat_router
from backend.api.documents import router as documents_router
from backend.api.escalation import router as escalation_router
from backend.api.family import router as family_router
from backend.api.higher_ed import router as higher_ed_router
from backend.api.natural_language_question import router as natural_language_question_router
from backend.api.profiling import router as profiling_router
from backend.api.secondary_tracks import router as secondary_tracks_router
from backend.api.session import router as session_router

router = APIRouter()
router.include_router(profiling_router)
router.include_router(natural_language_question_router)
router.include_router(chat_router)
router.include_router(secondary_tracks_router)
router.include_router(higher_ed_router)
router.include_router(session_router)
router.include_router(escalation_router)
router.include_router(family_router)
router.include_router(documents_router)
router.include_router(answers_router)
