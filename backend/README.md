# Backend

This repository slice contains the backend implementation work completed in this session for Possibilista.

## What exists now

### API

- `backend/api/profiling.py`
  - `POST /api/v1/profiling/interests`
  - Accepts `interests: list[str]` and `skipped: bool`
  - Enforces bearer auth
  - Enforces the `9.º ano` access rule
  - Persists interest selections or skip markers
  - Returns JSON with `status` and `message`

### Models

- `backend/models/base.py`
  - Shared SQLAlchemy declarative base with naming conventions
- `backend/models/student_session.py`
  - `StudentSession`
  - `id`
  - `school_year`
  - Relationships:
    - `student_interests`
    - `student_strength_weaknesses`
- `backend/models/student_interest.py`
  - `StudentInterest`
  - `id`
  - `session_id`
  - `interest`
  - `skipped`
  - Relationship back to `StudentSession`
- `backend/models/student_strength_weakness.py`
  - `StudentStrengthWeakness`
  - `id`
  - `session_id`
  - `strengths` as `text[]`
  - `weaknesses` as `text[]`
  - `partial`
  - Relationship back to `StudentSession`

### Migrations

- `migrations/versions/20260705_01_create_student_interest_table.py`
  - Creates `student_interest`
  - Adds FK to `student_session`
  - Adds `session_id` index
  - Adds a check constraint so skipped rows can exist without interest text
- `migrations/versions/20260705_02_create_student_strength_weakness_table.py`
  - Creates `student_strength_weakness`
  - Uses PostgreSQL text arrays for strengths and weaknesses
  - Adds FK to `student_session`
  - Adds `session_id` index

### Tests

- `tests/backend/test_student_interest.py`
  - Verifies the `StudentInterest` table shape and FK relation
- `tests/backend/test_profiling_interests.py`
  - Verifies payload parsing
  - Verifies 9.º ano gating
  - Verifies interest persistence and skip persistence
- `tests/backend/test_student_strength_weakness.py`
  - Verifies the `StudentStrengthWeakness` table shape, array types, and FK relation

## Session summary

Implemented during this session:

1. Student interest persistence model and migration
2. `POST /api/v1/profiling/interests`
3. Interest preferences React screen and tests
4. Student academic strengths/weaknesses model and migration
5. This backend README

## Notes

- The current checkout is intentionally thin and does not include the full production backend tree described in `apex.md`.
- The code added here is aligned to the Apex spec context available in `Apex Spec Context/`.
- Python dependency installation is not available in this environment, so runtime test execution was limited to syntax compilation checks.

