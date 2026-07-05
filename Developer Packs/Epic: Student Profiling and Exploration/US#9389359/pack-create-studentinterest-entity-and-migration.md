# Developer Pack — Create StudentInterest entity and migration
## Story: US#9389359 — Interest Preferences Collection

## Context
Tech stack: LangChain + FastAPI + PostgreSQL + pgvector + React. This task belongs to Story 9389359: Interest Preferences Collection. It involves defining the StudentInterest entity in the backend data model with fields interest (string), skipped (boolean), and a foreign key relation to StudentSession. Additionally, implement the database migration to create the corresponding table with appropriate constraints to store student interest preferences.

## Implementation Steps
1. In the backend data model module (e.g., models/student_interest.py or equivalent), define the StudentInterest ORM entity with fields: id (primary key), session_id (foreign key to StudentSession), interest (string), skipped (boolean).
2. Ensure the relation to StudentSession is properly configured as a many-to-one relationship (StudentInterest belongs to StudentSession).
3. Create a new Alembic migration script to add the student_interest table with columns: id (UUID or serial primary key), session_id (foreign key referencing student_session table), interest (string/text), skipped (boolean).
4. Add database constraints: session_id not null, interest nullable if skipped is true, skipped not null with default false if applicable.
5. Update the database schema by applying the migration to create the student_interest table.
6. Add any necessary indexing on session_id for query performance.
7. Verify that the entity definition and migration align with the existing StudentSession entity and database schema conventions.
8. Add unit tests or integration tests for the migration if project standards require it, ensuring the table is created with correct columns and constraints.

## Files to Change
- `backend/models/student_interest.py` — Add StudentInterest ORM entity definition with fields and relations.
- `migrations/versions/xxxx_add_student_interest_table.py` — Create Alembic migration script to add student_interest table with required columns and constraints.

## Test Assertions
- The database migration creates a student_interest table with columns for id, session_id, interest, and skipped.
- The student_interest table enforces a foreign key constraint on session_id referencing student_session.
- The StudentInterest entity correctly maps to the student_interest table with the specified fields and relation to StudentSession.

## Agentic Brief
**Task**: Create StudentInterest entity and migration
**Files**: `backend/models/student_interest.py`, `migrations/versions/xxxx_add_student_interest_table.py`
**Verify**: `alembic upgrade head && pytest tests/backend/test_models.py -k test_student_interest_entity`
**Constraints**:
- Use existing ORM and migration frameworks; no new dependencies.
- Follow existing database schema naming conventions and constraints.
- Ensure compliance with data protection regulations for student data.
- Maintain consistency with the StudentSession entity relation patterns.
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
**Story**: US#9389359 — Interest Preferences Collection
**Acceptance Criteria**:
### Story 9389359: Interest Preferences Collection

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 11:59 UTC

```gherkin
Feature: Interest Preferences Collection

  Scenario: Provide Interests Successfully
    Given the student is a 9.º ano student
    And the student is ready to answer interest questions
    When the student answers questions about their interests
    Then the system records the student's interest preferences for guidance

  Scenario: Skip Interest Questions
    Given the student is a 9.º ano student
    And the student is presented with interest questions
    When the student chooses not to answer the interest questions
    Then the system notes the lack of interest input
    And the system proceeds without interest data
```

**Your Task**: Create StudentInterest entity and migration
Define the StudentInterest entity in the data model with fields for interest, skipped flag, and relation to StudentSession. Implement the corresponding database migration to support storing student interest preferences as per the data model.

**Implementation Steps**:
1. In the backend data model module (e.g., models/student_interest.py or equivalent), define the StudentInterest ORM entity with fields: id (primary key), session_id (foreign key to StudentSession), interest (string), skipped (boolean).
2. Ensure the relation to StudentSession is properly configured as a many-to-one relationship (StudentInterest belongs to StudentSession).
3. Create a new Alembic migration script to add the student_interest table with columns: id (UUID or serial primary key), session_id (foreign key referencing student_session table), interest (string/text), skipped (boolean).
4. Add database constraints: session_id not null, interest nullable if skipped is true, skipped not null with default false if applicable.
5. Update the database schema by applying the migration to create the student_interest table.
6. Add any necessary indexing on session_id for query performance.
7. Verify that the entity definition and migration align with the existing StudentSession entity and database schema conventions.
8. Add unit tests or integration tests for the migration if project standards require it, ensuring the table is created with correct columns and constraints.

**Required Test Coverage**:
- The database migration creates a student_interest table with columns for id, session_id, interest, and skipped.
- The student_interest table enforces a foreign key constraint on session_id referencing student_session.
- The StudentInterest entity correctly maps to the student_interest table with the specified fields and relation to StudentSession.

## CLAUDE.md Snippet
### Active Task: Create StudentInterest entity and migration
**Story**: US#9389359 — Interest Preferences Collection
**Goal**: Define and implement the StudentInterest entity and database migration to store student interest preferences linked to student sessions.
**Key files**: `backend/models/student_interest.py`, `migrations/versions/xxxx_add_student_interest_table.py`
**Done when**: The student_interest table exists in the database with correct schema and the StudentInterest entity is defined with proper relations and fields.
*Delete this section once the task is complete.*
