"""FastAPI routers for Possibilista."""

from fastapi import APIRouter

from backend.api.chat import router as chat_router
from backend.api.higher_ed import router as higher_ed_router
from backend.api.natural_language_question import router as natural_language_question_router
from backend.api.profiling import router as profiling_router
from backend.api.secondary_tracks import router as secondary_tracks_router

router = APIRouter()
router.include_router(profiling_router)
router.include_router(natural_language_question_router)
router.include_router(chat_router)
router.include_router(secondary_tracks_router)
router.include_router(higher_ed_router)
