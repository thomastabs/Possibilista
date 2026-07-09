# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Possibilista is a conversational, multi-agent school-guidance web app for Portuguese secondary-school
students (9.º–12.º ano). Governing principle: **the LLM is the interface; official documents are the
source of truth** — answers are RAG-grounded, distinguish fact from interpretation, and route critical
decisions to human/institutional confirmation. Full product framing is in `README.md`.

Target architecture (per `README.md` / `Apex Spec Context/tech-stack.md`): a monolithic FastAPI backend
hosting LangChain agents (Orchestrator, Profiler, Secondary, Superior/Simulation), PostgreSQL + pgvector
for both relational data and RAG retrieval, and a Next.js/React frontend.

**Current repo state is a thin implementation slice**, not the full target system — see "What's actually
implemented" below before assuming any endpoint, agent, or infra piece exists.

## Spec-anchored workflow (read this before adding a feature)

This repo is being built through an external spec pipeline ("Apex"); the specs are the contract, and code
should conform to them rather than the other way around:

- `Apex Spec Context/functional-spec.md` — locked per-story Gherkin acceptance criteria (source of truth
  for behavior).
- `Apex Spec Context/technical-spec.md` — locked endpoint contracts (`METHOD /path · auth · in:{} · out:{}`)
  and the full data model. New endpoints/fields should match this exactly, including field names and auth
  mode, unless the spec itself is being amended.
- `Apex Spec Context/constraints.md` — project-wide NFRs in EARS notation (performance, security,
  reliability, etc.) — non-functional requirements new code should honour.
- `Apex Spec Context/tech-stack.md` — the locked stack decision and its tradeoffs.
- `Developer Packs/Epic: <name>/US#<story-id>/pack-*.md` — pre-written, task-level implementation briefs
  (context, approach, acceptance checklist) for stories not yet built. **Check here first** when asked to
  implement a story — the task may already have a detailed pack.

Only a subset of `technical-spec.md`'s endpoints are implemented (see below); the rest are future work
with packs already written for several of them.

## What's actually implemented

- **Backend** (`backend/`): FastAPI routers in `backend/api/`, SQLAlchemy 2.x async models in
  `backend/models/`, business logic in `backend/services/`.
  - `backend/api/profiling.py` — `POST /api/v1/profiling/interests`, `/motivations`,
    `/strengths-weaknesses`, `GET /api/v1/profiling/summary`.
  - `backend/api/natural_language_question.py` — `POST /api/v1/chat/natural-language-question`.
  - `backend/services/profile_summary.py` — aggregates interests/motivation/strengths into a summary +
    missing-field suggestions.
  - `backend/services/natural_language_question.py` — rule-based question classification
    (clear/ambiguous/out_of_scope) and document retrieval stub; no real RAG/LLM call yet.
  - There is **no `main.py`** / FastAPI app instantiation, and no CORS/auth middleware — routers assume
    `request.state.db` and `request.state.student_session` are injected by infra that doesn't exist yet in
    this slice (see `get_db_session`/`get_current_student_session` in `profiling.py`).
  - The "9.º ano only" access rule is enforced per-endpoint in `backend/api/profiling.py` (checked against
    `StudentSession.school_year`), not centrally.
- **Migrations** (`migrations/versions/`): Alembic scripts for `student_interest`,
  `student_strength_weakness`, `student_motivation` tables. **No `alembic.ini`** is checked in yet.
- **Frontend components** (`src/components/`): plain React/TypeScript screens (interest preferences,
  motivations, strengths/weaknesses, profile summary, natural-language question) with colocated tests in
  `src/components/__tests__/`. These call the backend directly via `fetch`, not through a shared API
  client.
  - Note: `frontend/` only contains a `package.json` (Next.js 15 + React 19 + Zustand + Tailwind deps,
    `test` script wired to `vitest`) — there is no Next.js app tree there yet. The actual components live
    at top-level `src/`, and their tests import `jest.fn()`/globals with no vitest/jest config file present
    in the repo. Running `npm test` will need a test config added first; don't assume it works out of the
    box.
- **Tests** (`tests/backend/`): plain `pytest` files, no `pytest.ini`/`conftest.py`. Async service/endpoint
  logic is exercised via `asyncio.run(...)` directly (no pytest-asyncio fixtures), and DB calls are faked
  with small hand-rolled stub classes (e.g. `DummyDB` in `test_profiling_interests.py`) rather than a real
  Postgres connection or FastAPI `TestClient` dependency overrides.

## Commands

Backend (from repo root, `backend/requirements.txt` lists pinned versions — no venv/lockfile is checked in
yet, so install into your own environment first):

```bash
pip install -r backend/requirements.txt
pytest tests/backend                      # run all backend tests
pytest tests/backend/test_profiling_interests.py -k test_record_student_interests_saves_values_for_ninth_grade
ruff check backend                        # lint (ruff is pinned in requirements.txt)
```

Frontend (`frontend/package.json` scripts — see the caveat above about missing test config):

```bash
cd frontend && npm install
npm run dev / build / start / lint
npm test                                  # vitest — needs a vitest/jsdom + testing-library setup first
```

## Conventions worth preserving

- Backend request payloads are hand-parsed and validated in `backend/api/profiling.py`
  (`_parse_*_payload` helpers) rather than via Pydantic request models — mirror this pattern for new
  `profiling`-style endpoints; `natural_language_question.py` uses a Pydantic `BaseModel` instead, so either
  style exists depending on which file you're extending.
- SQLAlchemy models share one declarative `Base` with explicit naming conventions
  (`backend/models/base.py`) — reuse it for any new table rather than declaring a fresh base.
- Endpoints that fail DB writes roll back and re-raise as `HTTPException(500)`; read failures inside
  aggregation logic (`profile_summary.py`) log and degrade gracefully (return empty/None) instead of
  raising — match whichever pattern fits the call site.
