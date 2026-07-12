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

## Prerequisites

**Docker must be installed and running before you attempt any of the local development steps
below.** Every section that follows — running PostgreSQL, running the backend, and verifying
the environment — assumes a working `docker` and `docker compose` on your machine. Skipping
this will make every later step fail.

- Install Docker for your platform: [Windows](https://docs.docker.com/desktop/install/windows-install/),
  [macOS](https://docs.docker.com/desktop/install/mac-install/), or
  [Linux](https://docs.docker.com/engine/install/) (Linux uses distribution-specific packages —
  see the linked guide for your distro).
- Verify the install before continuing:
  ```bash
  docker --version
  docker compose version
  ```
  Both must print a version. If either fails, see
  [`docs/local-development.md`](docs/local-development.md) for detailed install steps and
  troubleshooting (BIOS virtualization, WSL 2, Linux `docker` group permissions, restart
  requirements).

## Running PostgreSQL Locally (Docker)

> **Prerequisite:** Docker must be installed and running — see [Prerequisites](#prerequisites)
> above before continuing.

The backend expects PostgreSQL (with the pgvector extension) reachable at the connection
string in `backend/config.py`'s `database_url` default
(`postgresql+psycopg://possibilista:possibilista@localhost:5432/possibilista`). A
`Dockerfile` and `docker-compose.yml` at the repo root run it in a container with matching
default credentials: `docker-compose.yml`'s `postgres` service sets `POSTGRES_USER`,
`POSTGRES_PASSWORD`, and `POSTGRES_DB` to `possibilista`, `possibilista`, and `possibilista`
respectively — the same values baked into `backend/config.py`'s `database_url` default above,
so the backend can connect out of the box with no extra configuration. Override any of the
three via the shell environment or a `.env` file if you need different credentials.

Start it with the port-availability check script rather than calling Docker Compose
directly, so a port conflict fails fast with a clear message instead of a cryptic Docker
error:

```bash
./start_postgres.sh
```

This builds the image (based on `pgvector/pgvector:pg15`, not the plain `postgres` image,
so `CREATE EXTENSION vector` in the Alembic migrations succeeds) and runs
`docker compose up` (or `docker-compose up` if you only have the legacy binary installed).

### PostgreSQL Health Check

`docker-compose.yml`'s `postgres` service defines a healthcheck that runs `pg_isready` every 5
seconds (5 retries) — this is what the `backend` service's `depends_on: condition:
service_healthy` waits on before starting, so the backend never starts against a database
that isn't accepting connections yet.

To check the container's status and health yourself:

```bash
docker ps
```

Look for the `possibilista-postgres` container's `STATUS` column — it should read
`Up ... (healthy)` once `pg_isready` starts succeeding (typically within a few seconds of
startup). If it stays `(health: starting)` or flips to `(unhealthy)`, inspect the logs:

```bash
docker logs possibilista-postgres
```

### PostgreSQL Port Conflict Resolution

If port 5432 is already in use on your machine — another Postgres instance, a different
project's container, etc. — `start_postgres.sh` detects it before Docker even tries to bind
the port, and exits with a message telling you to either free the port or use a different
one. To use a different host port, set `POSTGRES_HOST_PORT` when starting:

```bash
POSTGRES_HOST_PORT=5433 ./start_postgres.sh
```

Or, if you're calling `docker compose` directly instead of the script:

```bash
POSTGRES_HOST_PORT=5433 docker compose up
```

Either form maps the container's internal port 5432 to `5433` on the host instead of the
default — `docker-compose.yml`'s `ports:` mapping already reads this variable, so no file
edits are needed. If you change the host port, update `backend/config.py`'s `database_url`
(or your `.env` override) to match, e.g. `...@localhost:5433/possibilista`.
