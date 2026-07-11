# PostgreSQL container for Possibilista (Story US#9402358).
#
# Base image is pgvector/pgvector:pg15 rather than the plain postgres:15 the pack asked
# for — the backend's Alembic migrations already run `CREATE EXTENSION IF NOT EXISTS vector`
# (see migrations/versions/20260711_03_create_document_table.py), which the vanilla
# PostgreSQL image doesn't provide. pgvector/pgvector:pg15 is the same official PostgreSQL 15
# image with the pgvector extension pre-built and installed, so `CREATE EXTENSION vector`
# succeeds without any extra setup step.
FROM pgvector/pgvector:pg15

# Default credentials match backend/config.py's default database_url exactly
# (postgresql+psycopg://possibilista:possibilista@localhost:5432/possibilista) so the
# container works out of the box with the backend's own defaults. Override any of these at
# runtime (`docker run -e POSTGRES_PASSWORD=... `) or via docker-compose.yml's environment
# section for anything beyond local development.
ENV POSTGRES_USER=possibilista
ENV POSTGRES_PASSWORD=possibilista
ENV POSTGRES_DB=possibilista

EXPOSE 5432
