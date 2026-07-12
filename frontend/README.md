# Possibilista Frontend

This directory contains the Next.js frontend package, tests, and Dockerfile.

## Local container setup

Use the root `docker-compose.yml` as the canonical local environment:

```bash
docker compose up --build
```

That command starts PostgreSQL, the FastAPI backend, and this frontend together. The
frontend listens on `http://localhost:3000` by default. Override the host port with
`FRONTEND_HOST_PORT`, for example:

```bash
FRONTEND_HOST_PORT=3001 docker compose up --build
```

See the root `README.md` for the full environment variable table and verification steps.

The frontend uses Next.js App Router under `frontend/app` and proxies `/api/v1/*` requests
to the backend through `frontend/next.config.ts`.

## Frontend-only Docker build

Build only the frontend image from the repository root:

```bash
./build_frontend_docker.sh
```

The script builds `possibilista-frontend:latest` from `./frontend`.

Before invoking Docker, the script checks that `frontend/Dockerfile` exists. If the Dockerfile is missing or misnamed, the script exits with a non-zero status and prints a clear error telling you where the Dockerfile is expected.

## Useful commands

```bash
npm install
npm run build
npm test
```
