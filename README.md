# Possibilista

## Purpose

Possibilista is a conversational, multi-agent school-guidance web application for secondary-school students in Portugal (9.º–12.º ano). It turns open, anxious
questions about academic futures into structured, source-grounded guidance: which secondary tracks exist, what disciplines and exams they require, and how
those choices open or close doors to higher-education courses.

The product's governing principle: **the language model is the interface; official
documents are the source of truth.** Every substantive answer is grounded in
official sources via retrieval (RAG), and the assistant explicitly distinguishes
documented fact from interpretation, says when it lacks a basis to answer, and
routes critical decisions to human/institutional confirmation.

## Target Users

- **Students (primary).** Three usage modes by school stage:
  - *Exploration (9.º ano):* discover interests, compare secondary areas, understand
    which doors each choice opens or closes.
  - *Management (10.º–12.º):* simulate disciplines, exams, averages, and
    compatibility with higher-education courses.
  - *Confirmation (special cases):* identify situations that require institutional
    confirmation (special regimes, equivalences, contingents, specific rules).
- **Families (encarregados de educação).** Secondary audience; need plain-language
  explanations and the ability to follow a student's explored path.
- **Schools.** Future audience for a platform tier with alerts and follow-up.

## Core Value Proposition

- **Accessibility** — first-layer orientation in plain language, available 24/7.
- **Equity** — reduces the advantage held by students with paid/private guidance.
- **Rigour** — answers anchored in official sources, not model recall.
- **Time** — hours of fragmented research compressed into minutes.

It is explicitly a *first* layer of orientation. It does not replace psychologists,
teachers, schools, IAVE/JNE or DGES; it does not guarantee future placements; and
it does not make critical decisions — it structures and informs them.

## System Shape (for downstream design phases)

A coordinated multi-agent system:

- **Orchestrator** — interprets intent, manages conversation state, decides which
  specialists to call, resolves contradictions, assembles the final answer.
- **Profiler agent** — explores interests, motivations, strong/weak disciplines,
  and areas to avoid.
- **Secondary agent (10.º–12.º)** — analyses secondary tracks, disciplines, and the
  valid combinations (trienais / bienais / anuais).
- **Superior agent (higher ed)** — cross-references tracks with courses, entrance
  exams (provas de ingresso) and their weights, and entry averages (médias).

Supporting concerns: session-only (non-persistent) memory holding name, age, school
year, interests, strong/weak disciplines, goals, explored track and explored
courses; a RAG retrieval layer (chunking → embeddings + vector index → retrieval →
grounded answer with sources); and explicit human-escalation paths.

## MVP Scope

9.º-ano exploration + LLM-generated profile + secondary-track exploration + standard
official sources + session memory. Deliberately bounded: out of scope for the MVP are
persistent cross-session memory, API-driven psychometric profiling, and the
school/family platform tier — those are later phases.

## Authoritative Sources (RAG corpus)

- Consolidated legal framework for secondary education.
- General Exam Guide 2026 (calendar, phases, registrations, deadlines).
- Secondary-track definitions (disciplines: trienais, bienais, anuais).
- Higher-education courses (entrance exams and compatibilities).

## Local Container Environment

The local Docker setup has one canonical entry point: `docker-compose.yml`. It defines the three development containers together:

- `postgres` — PostgreSQL 15 with pgvector, exposed on `localhost:5432` by default.
- `backend` — FastAPI served by Uvicorn, exposed on `localhost:8000` by default.
- `frontend` — Next.js production server, exposed on `localhost:3000` by default.

`docs/local-development.md` covers Docker installation and host-specific troubleshooting.
This section covers the project-specific environment.

### Prerequisites

Docker must be installed and running before any container command will work:

```bash
docker --version
docker compose version
```

Both commands must print a version. If either fails, install Docker from the official docs
for [Windows](https://docs.docker.com/desktop/install/windows-install/),
[macOS](https://docs.docker.com/desktop/install/mac-install/), or
[Linux](https://docs.docker.com/engine/install/), then revisit
[`docs/local-development.md`](docs/local-development.md).

### Environment Variables

The defaults are suitable for local development. Copy `.env.example` only if you want to
override ports, credentials, or URLs:

```bash
cp .env.example .env
```

Important variables:

| Variable | Default | Used by |
| --- | --- | --- |
| `POSTGRES_USER` | `possibilista` | Postgres container |
| `POSTGRES_PASSWORD` | `possibilista` | Postgres container |
| `POSTGRES_DB` | `possibilista` | Postgres container |
| `POSTGRES_HOST_PORT` | `5432` | Host-to-Postgres port mapping |
| `BACKEND_HOST_PORT` | `8000` | Host-to-backend port mapping |
| `FRONTEND_HOST_PORT` | `3000` | Host-to-frontend port mapping |
| `DATABASE_URL` | `postgresql+psycopg://possibilista:possibilista@postgres:5432/possibilista` | Backend container |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Frontend container |
| `BACKEND_INTERNAL_URL` | `http://backend:8000` | Frontend build/runtime API proxy |

Inside Compose, `DATABASE_URL` must use the service hostname `postgres`, not `localhost`.
For running backend code directly on the host, use the localhost form instead:
`postgresql+psycopg://possibilista:possibilista@localhost:5432/possibilista`.

### Database Migrations

The backend does not run migrations automatically on startup. After Postgres is healthy,
apply the schema before using API endpoints that write to the database:

```bash
DATABASE_URL=postgresql+psycopg://possibilista:possibilista@localhost:5432/possibilista \
  PYTHONPATH=. .venv/bin/alembic upgrade head
```

If you override `POSTGRES_HOST_PORT`, use that host port in the migration `DATABASE_URL`.

### Start Everything

From the repository root:

```bash
docker compose up --build
```

This builds and starts Postgres, the backend, and the frontend on one Compose network. The
backend waits for Postgres to pass its `pg_isready` healthcheck before starting. The frontend
service additionally requires a buildable Next.js app tree in `frontend/`.

To run in the background:

```bash
docker compose up --build --detach
```

To stop the stack:

```bash
docker compose down
```

To stop the stack and delete the persisted local Postgres data volume:

```bash
docker compose down --volumes
```

### Focused Container Commands

Use these when you only need one piece of the stack:

```bash
./start_postgres.sh
```

Starts the Postgres service with an early host-port conflict check.

```bash
./build_frontend_docker.sh
```

Builds the frontend image as `possibilista-frontend:latest` and checks that
`frontend/Dockerfile` exists before invoking Docker.

### Verify the Stack

Once `docker compose up --build` is running:

```bash
docker ps
curl http://localhost:8000/health
curl -I http://localhost:3000
```

Expected results:

- `possibilista-postgres` is `Up ... (healthy)`.
- `possibilista-backend` is `Up`.
- `possibilista-frontend` is `Up`.
- `curl http://localhost:8000/health` returns `{"status":"ok"}`.
- `curl -I http://localhost:3000` returns an HTTP response from Next.js.

### Ports and Conflicts

Override host ports without editing Compose:

```bash
POSTGRES_HOST_PORT=5433 BACKEND_HOST_PORT=8001 FRONTEND_HOST_PORT=3001 docker compose up --build
```

If you change `POSTGRES_HOST_PORT` while running backend code directly on the host, update
the host-side `DATABASE_URL` to use the same port.

### Logs and Troubleshooting

```bash
docker logs possibilista-postgres
docker logs possibilista-backend
docker logs possibilista-frontend
```

- If Postgres is unhealthy, inspect `possibilista-postgres` logs first.
- If the backend exits immediately, check for a missing or empty `DATABASE_URL`.
- If the frontend image build fails because `frontend/Dockerfile` is missing or misnamed,
  use `./build_frontend_docker.sh` for the clearer preflight error.
- If API requests through the frontend fail, check that `BACKEND_INTERNAL_URL` points to
  `http://backend:8000` for Compose builds.
- If Docker reports that it cannot connect to the daemon, start Docker Desktop or the Docker
  service before rerunning Compose.
