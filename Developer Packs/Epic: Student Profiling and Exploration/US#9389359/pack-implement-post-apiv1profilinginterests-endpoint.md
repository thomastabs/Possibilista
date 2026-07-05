# Developer Pack — Implement POST /api/v1/profiling/interests endpoint
## Story: US#9389359 — Interest Preferences Collection

## Context
Tech stack: LangChain + FastAPI + PostgreSQL + pgvector + React. This task belongs to Story 9389359: Interest Preferences Collection. It involves implementing the POST /api/v1/profiling/interests endpoint which accepts a list of interests or a skipped flag from authenticated 9.º ano students, stores the interests or skip indication in the StudentInterest table, and returns a status and message accordingly.

## Implementation Steps
1. Modify backend/api/profiling.py (or the appropriate FastAPI router module) to add the POST /api/v1/profiling/interests endpoint with bearer authentication.
2. In the endpoint handler, accept JSON input with fields: interests (list of strings) and skipped (boolean).
3. Validate that the authenticated user is a 9.º ano student by checking their StudentSession record's school_year field (must be 9). Return 403 if not.
4. If skipped is true, create a StudentInterest record with skipped=True and no interest value for the current session_id.
5. If skipped is false, iterate over the interests list and create a StudentInterest record for each interest with skipped=False, linked to the current session_id.
6. Use the existing StudentInterest ORM entity defined in backend/models/student_interest.py for database operations.
7. Commit the new StudentInterest records to the PostgreSQL database asynchronously using the existing database session.
8. Return a JSON response with status='success' and a message indicating interests were recorded or skipped accordingly.
9. Add error handling for missing or invalid input fields and database errors, returning appropriate HTTP status codes and messages.

## Files to Change
- `backend/api/profiling.py` — Add POST /api/v1/profiling/interests endpoint implementation handling interests submission or skip, validating 9.º ano student, and storing StudentInterest records.

## Test Assertions
- POST /api/v1/profiling/interests with valid interests and authenticated 9.º ano student stores interests and returns success status and message.
- POST /api/v1/profiling/interests with skipped=true and authenticated 9.º ano student records skip and returns success status and message.
- POST /api/v1/profiling/interests by non-9.º ano student returns 403 Forbidden.
- POST /api/v1/profiling/interests with missing or invalid input returns 400 Bad Request with error message.

## Agentic Brief
**Task**: Implement POST /api/v1/profiling/interests endpoint
**Files**: `backend/api/profiling.py`
**Verify**: `pytest tests/backend/test_student_interest.py`
**Constraints**:
- Enforce bearer authentication as per existing middleware.
- Use existing StudentInterest ORM entity and database session management.
- Validate student school year to ensure only 9.º ano students can submit interests.
- Return clear status and message in JSON response.
- Handle errors gracefully with appropriate HTTP status codes.
- Do not duplicate entity or migration code already implemented.
- Follow project coding and logging conventions for maintainability and observability.
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

**Your Task**: Implement POST /api/v1/profiling/interests endpoint
Develop the POST /api/v1/profiling/interests endpoint to accept a list of interests or a skipped flag from authenticated 9.º ano students. The endpoint should store the interests or note the skip in the StudentInterest table and return status and message accordingly.

**Implementation Steps**:
1. Modify backend/api/profiling.py (or the appropriate FastAPI router module) to add the POST /api/v1/profiling/interests endpoint with bearer authentication.
2. In the endpoint handler, accept JSON input with fields: interests (list of strings) and skipped (boolean).
3. Validate that the authenticated user is a 9.º ano student by checking their StudentSession record's school_year field (must be 9). Return 403 if not.
4. If skipped is true, create a StudentInterest record with skipped=True and no interest value for the current session_id.
5. If skipped is false, iterate over the interests list and create a StudentInterest record for each interest with skipped=False, linked to the current session_id.
6. Use the existing StudentInterest ORM entity defined in backend/models/student_interest.py for database operations.
7. Commit the new StudentInterest records to the PostgreSQL database asynchronously using the existing database session.
8. Return a JSON response with status='success' and a message indicating interests were recorded or skipped accordingly.
9. Add error handling for missing or invalid input fields and database errors, returning appropriate HTTP status codes and messages.

**Required Test Coverage**:
- POST /api/v1/profiling/interests with valid interests and authenticated 9.º ano student stores interests and returns success status and message.
- POST /api/v1/profiling/interests with skipped=true and authenticated 9.º ano student records skip and returns success status and message.
- POST /api/v1/profiling/interests by non-9.º ano student returns 403 Forbidden.
- POST /api/v1/profiling/interests with missing or invalid input returns 400 Bad Request with error message.

## CLAUDE.md Snippet
### Active Task: Implement POST /api/v1/profiling/interests endpoint
**Story**: US#9389359 — Interest Preferences Collection
**Goal**: Implement the POST /api/v1/profiling/interests endpoint to store or skip student interest preferences for authenticated 9.º ano students.
**Key files**: `backend/api/profiling.py`
**Done when**: POST /api/v1/profiling/interests correctly stores interests or skip flag for authenticated 9.º ano students and returns appropriate success responses.
*Delete this section once the task is complete.*
