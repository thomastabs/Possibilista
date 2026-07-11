"""Application configuration loaded from environment variables / .env."""

from __future__ import annotations

import logging
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://possibilista:possibilista@localhost:5432/possibilista"
    cors_origins: list[str] = ["http://localhost:3000"]

    # Reserved for the LangGraph agent integrations described in
    # Apex Spec Context/tech-stack.md (Orchestrator/Profiler/Secondary/Simulation) — no code
    # path in this repo slice actually calls any of these APIs yet (see
    # DETERMINISTIC_STUBS.md: every RAG/LLM-shaped surface is a deterministic stub), so these
    # are optional and intentionally excluded from REQUIRED_ENVIRONMENT_VARIABLES below.
    # Declared here so the container's environment contract already has a place for them.
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    google_api_key: str | None = None
    ai_key_encryption_secret: str | None = None


settings = Settings()

# DATABASE_URL is the only environment variable actually load-bearing right now: Settings'
# default points at `localhost`, which only resolves inside a container if Postgres runs in
# the same one — in the Docker Compose setup (Story 9402358/9402359) the backend and
# postgres containers are separate hosts on the Compose network, so DATABASE_URL must be
# overridden to the `postgres` service name. Falling through to the localhost default would
# fail to connect with whatever error SQLAlchemy raises first, rather than a clear one, so
# this is validated explicitly at container startup.
REQUIRED_ENVIRONMENT_VARIABLES = ("DATABASE_URL",)


def validate_required_environment_variables() -> None:
    """Exit with a clear error if any required environment variable is unset.

    Checks the raw process environment rather than the already-constructed ``settings``
    object, since a Settings field's default would otherwise mask a genuinely-missing
    variable (Story 9402359, scenario 2).
    """

    missing = [name for name in REQUIRED_ENVIRONMENT_VARIABLES if not os.environ.get(name)]
    if missing:
        logger.error(
            "Missing required environment variable(s): %s. Set them before starting the "
            "backend (see docker-compose.yml's backend service or README.md).",
            ", ".join(missing),
        )
        raise SystemExit(1)
