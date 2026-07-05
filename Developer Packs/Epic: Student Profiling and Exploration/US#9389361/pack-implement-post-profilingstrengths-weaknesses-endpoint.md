# Developer Pack — Implement POST /profiling/strengths-weaknesses endpoint
## Story: US#9389361 — Academic Strengths and Weaknesses Indication

## Context
Tech stack: LangChain + FastAPI + PostgreSQL + pgvector + React. This task belongs to story #9389361 Academic Strengths and Weaknesses Indication. It involves implementing the POST /api/v1/profiling/strengths-weaknesses endpoint to accept authenticated input of academic strengths, weaknesses, and a partial flag from 9.º ano students, storing this data in the StudentStrengthWeakness entity, and triggering recommendation logic for compatible secondary tracks based on the input.

## Implementation Steps
1. Modify backend/api/profiling.py to add a POST endpoint at /api/v1/profiling/strengths-weaknesses with bearer token authentication.
2. In the endpoint handler, validate the incoming JSON payload containing strengths (list of strings), weaknesses (list of strings), and partial (boolean).
3. Retrieve the authenticated student's session from the database using the bearer token context to associate the data correctly.
4. Create or update the StudentStrengthWeakness record linked to the student's session with the provided strengths, weaknesses, and partial flag.
5. Invoke the existing recommendation logic for compatible secondary tracks based on the stored strengths and weaknesses (assumed implemented in sibling task).
6. Return a JSON response with status and message indicating success or any validation errors.
7. Add error handling for invalid input types or missing required fields, returning appropriate HTTP 400 responses.
8. Ensure logging of the request and recommendation invocation for observability and traceability per NFR-7.
9. Write or extend backend tests to cover valid and partial input scenarios, verifying database persistence and correct response structure.
10. Document the endpoint in backend/api/__init__.py or relevant API docs to reflect the new endpoint and its contract.

## Files to Change
- `backend/api/profiling.py` — Add POST /api/v1/profiling/strengths-weaknesses endpoint handler with input validation, database persistence to StudentStrengthWeakness, and call to recommendation logic.
- `tests/backend/test_profiling_strengths_weaknesses.py` — Create new test file with tests for POST /profiling/strengths-weaknesses endpoint covering full and partial input cases, authentication, and response validation.

## Test Assertions
- POST /api/v1/profiling/strengths-weaknesses with valid strengths, weaknesses, and partial=false stores data and triggers compatible secondary track recommendations successfully.
- POST /api/v1/profiling/strengths-weaknesses with partial=true accepts incomplete data and proceeds without error, returning appropriate status and message.

## Agentic Brief
**Task**: Implement POST strengths-weaknesses endpoint
**Files**: `backend/api/profiling.py`, `tests/backend/test_profiling_strengths_weaknesses.py`
**Verify**: `pytest tests/backend/test_profiling_strengths_weaknesses.py`
**Constraints**:
- Reuse existing authentication middleware for bearer token validation.
- Use existing ORM model StudentStrengthWeakness for persistence; do not redefine model or migration.
- Invoke already implemented recommendation logic for compatible secondary tracks; do not reimplement it here.
- Follow existing API response patterns for status and message fields.
- Log retrieval queries and agent decisions for observability per NFR-7.
- Ensure input validation prevents malformed data storage and returns clear error messages.
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

**Your Task**: Implement POST /profiling/strengths-weaknesses endpoint
Develop the POST /api/v1/profiling/strengths-weaknesses endpoint to accept strengths, weaknesses, and partial flag from authenticated 9.º ano students. Validate input, store data in StudentStrengthWeakness entity, and trigger logic to recommend compatible secondary tracks based on provided strengths and weaknesses.

**Implementation Steps**:
1. Modify backend/api/profiling.py to add a POST endpoint at /api/v1/profiling/strengths-weaknesses with bearer token authentication.
2. In the endpoint handler, validate the incoming JSON payload containing strengths (list of strings), weaknesses (list of strings), and partial (boolean).
3. Retrieve the authenticated student's session from the database using the bearer token context to associate the data correctly.
4. Create or update the StudentStrengthWeakness record linked to the student's session with the provided strengths, weaknesses, and partial flag.
5. Invoke the existing recommendation logic for compatible secondary tracks based on the stored strengths and weaknesses (assumed implemented in sibling task).
6. Return a JSON response with status and message indicating success or any validation errors.
7. Add error handling for invalid input types or missing required fields, returning appropriate HTTP 400 responses.
8. Ensure logging of the request and recommendation invocation for observability and traceability per NFR-7.
9. Write or extend backend tests to cover valid and partial input scenarios, verifying database persistence and correct response structure.
10. Document the endpoint in backend/api/__init__.py or relevant API docs to reflect the new endpoint and its contract.

**Required Test Coverage**:
- POST /api/v1/profiling/strengths-weaknesses with valid strengths, weaknesses, and partial=false stores data and triggers compatible secondary track recommendations successfully.
- POST /api/v1/profiling/strengths-weaknesses with partial=true accepts incomplete data and proceeds without error, returning appropriate status and message.

## CLAUDE.md Snippet
### Active Task: Implement POST /profiling/strengths-weaknesses endpoint
**Story**: US#9389361 — Academic Strengths and Weaknesses Indication
**Goal**: Implement the POST /api/v1/profiling/strengths-weaknesses endpoint to accept, validate, and store academic strengths and weaknesses, triggering compatible secondary track recommendations.
**Key files**: `backend/api/profiling.py`, `tests/backend/test_profiling_strengths_weaknesses.py`
**Done when**: POST /api/v1/profiling/strengths-weaknesses endpoint stores input data and triggers recommendations, returning success status for both complete and partial inputs.
*Delete this section once the task is complete.*
