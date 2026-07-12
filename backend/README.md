# Possibilista Backend

This directory contains the FastAPI backend package, SQLAlchemy models, services, and
container definition for Possibilista.

## Local container setup

Use the root `docker-compose.yml` as the canonical local environment:

```bash
docker compose up --build
```

That command starts:

- PostgreSQL with pgvector from the root `Dockerfile`
- the FastAPI backend from `backend/Dockerfile`
- the Next.js frontend from `frontend/Dockerfile`

The backend listens on `http://localhost:8000` by default. Verify it with:

```bash
curl http://localhost:8000/health
```

See the root `README.md` for the full environment variable table, port overrides, and
troubleshooting notes.

## Backend-only notes

- `DATABASE_URL` is required at container startup.
- In Docker Compose, use the `postgres` service hostname:
  `postgresql+psycopg://possibilista:possibilista@postgres:5432/possibilista`.
- When running backend code directly on the host, use `localhost` instead:
  `postgresql+psycopg://possibilista:possibilista@localhost:5432/possibilista`.
- The current implementation uses deterministic RAG/LLM stubs; see `DETERMINISTIC_STUBS.md`
  before assuming live LangGraph, embedding, or LLM calls.

## Useful commands

```bash
PYTHONPATH=. pytest tests/backend
ruff check backend
```
