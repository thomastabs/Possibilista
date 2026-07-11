# Backend container for Possibilista's FastAPI application (Story US#9402359).
#
# Lives at backend/Dockerfile rather than the repo-root Dockerfile the pack suggested —
# that path is already taken by the PostgreSQL container's Dockerfile (Story US#9402358).
# Build context is still the repo root (see docker-compose.yml's backend service), since
# this needs to COPY both backend/ and migrations/.
FROM python:3.12-slim

# Unbuffered stdout/stderr so container logs — including the environment-variable
# validation error in backend/config.py — appear immediately instead of being buffered.
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first so this layer is cached across source-only changes.
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the backend source tree (routers, models, services, config) and the Alembic
# migrations it references.
COPY backend/ backend/
COPY migrations/ migrations/

EXPOSE 8000

# backend/main.py (backend.main:app, not backend.app.main:app — this repo has no
# backend/app/ package) calls backend/config.py's validate_required_environment_variables()
# before constructing the FastAPI app, so a container started without DATABASE_URL set exits
# immediately with a clear error instead of silently falling back to the local-dev default
# (which points at `localhost`, unreachable from inside this container).
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
