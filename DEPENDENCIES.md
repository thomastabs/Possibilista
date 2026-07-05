# Project Dependencies

This document translates the stack described in `Apex Spec Context/tech-stack.md` into the project dependencies that the codebase needs.

## Backend Runtime

- Python 3.12
- FastAPI
- Uvicorn or another ASGI server
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- PostgreSQL driver for async access
- LangChain
- Anthropic Claude SDK or API client integration
- OpenAI SDK or API client integration
- Google Gemini SDK or API client integration

## Backend Data Layer

- PostgreSQL
- pgvector

## Backend Support Libraries

- HTTP client library for external API calls
- Logging and observability utilities
- Authentication and security helpers
- CORS middleware support
- Environment/configuration loading

## Frontend Runtime

- Next.js 15 App Router
- React
- TypeScript
- React Query 5
- Zustand
- Tailwind CSS

## Frontend Support Libraries

- Fetch/API client wrappers for backend calls
- Form and state management helpers where needed
- UI primitives and accessible component utilities

## Development and Testing

- pytest
- Frontend test runner compatible with the Next.js stack
- Type checking for TypeScript
- Linting/formatting toolchain
- Alembic migration tooling

## Deployment and Infrastructure

- Docker
- GitHub Actions
- Azure Container Apps
- Azure File Share

## Optional Integrations

- GitHub repository context sync
- Figma context sync
- Taiga project management integration
- Jira project management integration

## Notes

- This list is derived from the stack and architecture described in `Apex Spec Context/tech-stack.md` and the surrounding Apex context files.
- The current checkout is a thin implementation slice, so it does not yet contain the full `package.json` / `pyproject.toml` / lockfile inventory.
- When the actual backend and frontend manifests are added, this document should be reconciled against the pinned versions there.

