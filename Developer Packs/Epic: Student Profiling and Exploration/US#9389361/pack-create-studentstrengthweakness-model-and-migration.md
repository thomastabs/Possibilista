# Developer Pack — Create StudentStrengthWeakness model and migration
## Story: US#9389361 — Academic Strengths and Weaknesses Indication

## Context
Tech stack: LangChain + FastAPI + PostgreSQL + pgvector + React. This task belongs to story #9389361 Academic Strengths and Weaknesses Indication. It involves defining the StudentStrengthWeakness model with fields strengths (list of strings), weaknesses (list of strings), partial (boolean), and a foreign key session_id to StudentSession. Also implement the corresponding database migration to create the table with proper relations.

## Implementation Steps
1. In backend/models/student_strength_weakness.py, define the StudentStrengthWeakness ORM model class with fields: id (primary key), session_id (foreign key to StudentSession.session_id), strengths (list of strings), weaknesses (list of strings), partial (boolean).
2. Ensure the model includes relationship back to StudentSession and uses appropriate PostgreSQL array type for strengths and weaknesses fields.
3. Create a new Alembic migration script in migrations/versions/ to create the student_strength_weakness table with columns: id (primary key), session_id (foreign key referencing student_session.session_id), strengths (text array), weaknesses (text array), partial (boolean).
4. Add foreign key constraint on session_id to student_session table with cascade delete behavior if applicable.
5. Update backend/models/__init__.py to import and expose the new StudentStrengthWeakness model.
6. Add unit tests in tests/backend/test_student_strength_weakness.py to verify ORM model creation, field types, and relationship to StudentSession.
7. Verify that the migration script runs successfully and creates the table with correct schema and constraints.
8. Ensure that the model and migration comply with NFR-8 encryption requirements for sensitive data at rest, applying encryption if existing patterns are used for other models.
9. Document the new model and migration in backend/README.md or equivalent developer documentation if present.
10. Run all backend tests to confirm no regressions and that the new model integrates correctly with existing session and profiling models.

## Files to Change
- `backend/models/student_strength_weakness.py` — Add StudentStrengthWeakness ORM model definition with specified fields and relations.
- `migrations/versions/20260705_02_create_student_strength_weakness_table.py` — Add Alembic migration script to create student_strength_weakness table with fields and foreign key constraint.
- `backend/models/__init__.py` — Import StudentStrengthWeakness model to expose it for use in the application.
- `tests/backend/test_student_strength_weakness.py` — Add tests for StudentStrengthWeakness model creation, field validation, and relation to StudentSession.

## Test Assertions
- The StudentStrengthWeakness model is defined with strengths, weaknesses as list of strings, partial as boolean, and session_id as foreign key to StudentSession.
- The Alembic migration creates the student_strength_weakness table with correct columns, types, and foreign key constraints.
- The migration runs successfully without errors and the table schema matches the model definition.
- The StudentStrengthWeakness model correctly relates to StudentSession and supports ORM operations.
- Sensitive data fields are stored encrypted at rest according to project security standards.

## Agentic Brief
**Task**: Create StudentStrengthWeakness model and migration
**Files**: `backend/models/student_strength_weakness.py`, `migrations/versions/20260705_02_create_student_strength_weakness_table.py`, `backend/models/__init__.py`, `tests/backend/test_student_strength_weakness.py`
**Verify**: `pytest tests/backend/test_student_strength_weakness.py`
**Constraints**:
- Reuse existing encryption middleware/patterns for sensitive data in PostgreSQL.
- Follow existing ORM and migration conventions in the codebase.
- Do not duplicate work from other tasks in the story.
- Ensure compliance with data protection regulations (NFR-9).
- Maintain consistency with existing StudentSession relations and naming conventions.
**Done when**: all Test Assertions pass and no pre-existing tests break.

## Chat Prompt
You are implementing a specific task in a software project.

**Tech Stack**: LangChain + FastAPI + PostgreSQL + pgvector + React

A monolithic Python backend built with FastAPI hosts all LangChain agents (Profiler, Orchestrator, Secondary, Simulation Engine) and exposes REST endpoints to a React single-page application. PostgreSQL with the pgvector extension serves as both the relational store for document metadata, version labels, and simulation inputs, and as the vector store for RAG retrieval. This option minimises infrastructure complexity and is the fastest path to a working end-to-end prototype.

- **Pro:** Single deployable unit; minimal DevOps overhead
- **Pro:** pgvector eliminates a separate vector-database dependency
- **Pro:** LangChain agent chains and RAG pipelines coexist in one codebase
- **Pro:** FastAPI async support handles concurrent chat sessions adequately at low-to-medium load
- **Con:** All agents share the same process; a spike in simulation requests can starve conversational agents
- **Con:** Scaling requires vertical growth or full-service replication rather than per-component scaling
- **Con:** Document ingestion pipeline runs in-process, risking request timeouts on large uploads
**Story**: US#9389361 — Academic Strengths and Weaknesses Indication
**Acceptance Criteria**:
### Story 9389361: Academic Strengths and Weaknesses Indication

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 11:59 UTC

```gherkin
Feature: Academic Strengths and Weaknesses Indication

  Scenario: Provide Strengths and Weaknesses Clearly
    Given the student is a 9.º ano student
    And the student is ready to indicate academic strengths and weaknesses
    When the student identifies their strong and weak disciplines
    Then the system uses the information to recommend compatible secondary tracks

  Scenario: Provide Incomplete or Unclear Strengths/Weaknesses
    Given the student is a 9.º ano student
    And the student is presented with questions about academic strengths and weaknesses
    When the student provides partial or vague information about strengths and weaknesses
    Then the system requests clarification or proceeds with limited data
```

**Your Task**: Create StudentStrengthWeakness model and migration
Define the StudentStrengthWeakness entity with fields strengths (list of strings), weaknesses (list of strings), partial (boolean), and session_id as a foreign key to StudentSession. Implement the corresponding database migration to create the table and ensure relations are properly set up.

**Implementation Steps**:
1. In backend/models/student_strength_weakness.py, define the StudentStrengthWeakness ORM model class with fields: id (primary key), session_id (foreign key to StudentSession.session_id), strengths (list of strings), weaknesses (list of strings), partial (boolean).
2. Ensure the model includes relationship back to StudentSession and uses appropriate PostgreSQL array type for strengths and weaknesses fields.
3. Create a new Alembic migration script in migrations/versions/ to create the student_strength_weakness table with columns: id (primary key), session_id (foreign key referencing student_session.session_id), strengths (text array), weaknesses (text array), partial (boolean).
4. Add foreign key constraint on session_id to student_session table with cascade delete behavior if applicable.
5. Update backend/models/__init__.py to import and expose the new StudentStrengthWeakness model.
6. Add unit tests in tests/backend/test_student_strength_weakness.py to verify ORM model creation, field types, and relationship to StudentSession.
7. Verify that the migration script runs successfully and creates the table with correct schema and constraints.
8. Ensure that the model and migration comply with NFR-8 encryption requirements for sensitive data at rest, applying encryption if existing patterns are used for other models.
9. Document the new model and migration in backend/README.md or equivalent developer documentation if present.
10. Run all backend tests to confirm no regressions and that the new model integrates correctly with existing session and profiling models.

**Required Test Coverage**:
- The StudentStrengthWeakness model is defined with strengths, weaknesses as list of strings, partial as boolean, and session_id as foreign key to StudentSession.
- The Alembic migration creates the student_strength_weakness table with correct columns, types, and foreign key constraints.
- The migration runs successfully without errors and the table schema matches the model definition.
- The StudentStrengthWeakness model correctly relates to StudentSession and supports ORM operations.
- Sensitive data fields are stored encrypted at rest according to project security standards.

## CLAUDE.md Snippet
### Active Task: Create StudentStrengthWeakness model and migration
**Story**: US#9389361 — Academic Strengths and Weaknesses Indication
**Goal**: Define and implement the StudentStrengthWeakness model and database migration to support storing academic strengths and weaknesses linked to student sessions.
**Key files**: `backend/models/student_strength_weakness.py`, `migrations/versions/20260705_02_create_student_strength_weakness_table.py`, `backend/models/__init__.py`, `tests/backend/test_student_strength_weakness.py`
**Done when**: The StudentStrengthWeakness model and migration are implemented and tested, with the database table created correctly and relations established.
*Delete this section once the task is complete.*
