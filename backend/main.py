"""FastAPI application entrypoint for Possibilista."""

from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from backend.api import router as api_router
from backend.config import settings
from backend.db import async_session_factory, engine
from backend.models.student_session import StudentSession

app = FastAPI(title="Possibilista")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Open a DB session per request and resolve the bearer token to a StudentSession.

    The bearer token *is* the student session id: every endpoint in this codebase
    already treats an unrecognized session_id as unauthorized, so this keeps that
    behavior consistent for the handful of endpoints (in profiling.py) that expect
    request.state.student_session instead of taking session_id explicitly.
    """
    async with async_session_factory() as session:
        request.state.db = session

        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header[len("bearer ") :].strip()
            try:
                token_uuid = UUID(token)
            except ValueError:
                token_uuid = None

            if token_uuid is not None:
                result = await session.execute(
                    select(StudentSession).where(StudentSession.id == token_uuid)
                )
                student_session = result.scalar_one_or_none()
                if student_session is not None:
                    request.state.student_session = student_session

        response = await call_next(request)
        return response


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await engine.dispose()


app.include_router(api_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
