"""Application configuration loaded from environment variables / .env."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://possibilista:possibilista@localhost:5432/possibilista"
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
