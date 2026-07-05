# Developer Pack — Develop recommendation logic for compatible secondary tracks
## Story: US#9389361 — Academic Strengths and Weaknesses Indication

## Context
Tech stack: LangChain + FastAPI + PostgreSQL + pgvector + React. This task belongs to story #9389361 Academic Strengths and Weaknesses Indication. It involves implementing backend recommendation logic that analyzes the student's academic strengths and weaknesses stored in the StudentStrengthWeakness entity to recommend compatible secondary tracks. This logic is invoked by the POST /api/v1/profiling/strengths-weaknesses endpoint and must handle both complete and partial data scenarios, either requesting clarification or proceeding accordingly.

## Implementation Steps
1. In backend/api/profiling.py, implement a new internal function `recommend_compatible_secondary_tracks` that accepts strengths (list[str]), weaknesses (list[str]), and partial (bool) as parameters and returns a list of compatible SecondaryTrack IDs or messages indicating need for clarification.
2. Within this function, query the database for SecondaryTrack entities and their associated disciplines (SecondaryTrackDiscipline) to evaluate compatibility based on the student's strengths and weaknesses. Define compatibility rules such as: tracks requiring disciplines in student's strengths are preferred; tracks with disciplines in weaknesses are deprioritized or excluded.
3. If the partial flag is true or the input data is insufficient to confidently recommend tracks, the function should return a response indicating that clarification is needed or proceed with limited recommendations with appropriate messaging.
4. Modify the existing POST /api/v1/profiling/strengths-weaknesses endpoint handler in backend/api/profiling.py to call `recommend_compatible_secondary_tracks` after saving the StudentStrengthWeakness data, and include the recommendation results or clarification requests in the response message.
5. Ensure the recommendation logic respects performance constraints by optimizing database queries and avoiding heavy computation in the request thread, possibly caching or limiting the scope of evaluation.
6. Add logging in the recommendation logic to record inputs and decisions for observability and traceability, complying with NFR-7.
7. Add unit tests in tests/backend/test_profiling_strengths_weaknesses.py to verify that given various strengths, weaknesses, and partial flags, the recommendation logic returns expected compatible tracks or clarification prompts.
8. Test that the endpoint returns appropriate status and messages when complete or partial data is submitted, and that the StudentStrengthWeakness entity is correctly updated.
9. Verify that the recommendation logic does not expose any unauthorized data and respects authentication and authorization constraints (NFR-1).

## Files to Change
- `backend/api/profiling.py` — Add `recommend_compatible_secondary_tracks` function implementing compatibility logic based on strengths and weaknesses; modify POST /api/v1/profiling/strengths-weaknesses endpoint to invoke this logic and include recommendations or clarification messages in the response.
- `tests/backend/test_profiling_strengths_weaknesses.py` — Add tests covering recommendation logic for complete and partial academic strengths and weaknesses input, verifying endpoint responses and database persistence.

## Test Assertions
- POST /api/v1/profiling/strengths-weaknesses with complete strengths and weaknesses returns compatible secondary tracks recommendations.
- POST /api/v1/profiling/strengths-weaknesses with partial or vague strengths and weaknesses returns a request for clarification or proceeds with limited recommendations.
- StudentStrengthWeakness entity is correctly created or updated with submitted strengths, weaknesses, and partial flag.
- Recommendation logic respects authentication and does not expose unauthorized data.
- Recommendation logic logs inputs and decisions for traceability.

## Agentic Brief
**Task**: Implement recommendation logic for compatible secondary tracks
**Files**: `backend/api/profiling.py`, `tests/backend/test_profiling_strengths_weaknesses.py`
**Verify**: `pytest tests/backend/test_profiling_strengths_weaknesses.py`
**Constraints**:
- Reuse existing backend/api/profiling.py and StudentStrengthWeakness model; do not add new dependencies.
- Ensure compliance with data protection regulations (NFR-9) and secure access controls (NFR-1).
- Log recommendation decisions for observability (NFR-7).
- Handle partial data gracefully, requesting clarification or proceeding with limited recommendations as per acceptance criteria.
- Optimize database queries to meet performance constraints (NFR-2, NFR-12).
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

**Your Task**: Develop recommendation logic for compatible secondary tracks
Implement backend logic that uses the student's academic strengths and weaknesses to recommend compatible secondary tracks. This logic will be invoked by the POST /profiling/strengths-weaknesses endpoint and must handle both complete and partial data scenarios, requesting clarification or proceeding accordingly.

**Implementation Steps**:
1. In backend/api/profiling.py, implement a new internal function `recommend_compatible_secondary_tracks` that accepts strengths (list[str]), weaknesses (list[str]), and partial (bool) as parameters and returns a list of compatible SecondaryTrack IDs or messages indicating need for clarification.
2. Within this function, query the database for SecondaryTrack entities and their associated disciplines (SecondaryTrackDiscipline) to evaluate compatibility based on the student's strengths and weaknesses. Define compatibility rules such as: tracks requiring disciplines in student's strengths are preferred; tracks with disciplines in weaknesses are deprioritized or excluded.
3. If the partial flag is true or the input data is insufficient to confidently recommend tracks, the function should return a response indicating that clarification is needed or proceed with limited recommendations with appropriate messaging.
4. Modify the existing POST /api/v1/profiling/strengths-weaknesses endpoint handler in backend/api/profiling.py to call `recommend_compatible_secondary_tracks` after saving the StudentStrengthWeakness data, and include the recommendation results or clarification requests in the response message.
5. Ensure the recommendation logic respects performance constraints by optimizing database queries and avoiding heavy computation in the request thread, possibly caching or limiting the scope of evaluation.
6. Add logging in the recommendation logic to record inputs and decisions for observability and traceability, complying with NFR-7.
7. Add unit tests in tests/backend/test_profiling_strengths_weaknesses.py to verify that given various strengths, weaknesses, and partial flags, the recommendation logic returns expected compatible tracks or clarification prompts.
8. Test that the endpoint returns appropriate status and messages when complete or partial data is submitted, and that the StudentStrengthWeakness entity is correctly updated.
9. Verify that the recommendation logic does not expose any unauthorized data and respects authentication and authorization constraints (NFR-1).

**Required Test Coverage**:
- POST /api/v1/profiling/strengths-weaknesses with complete strengths and weaknesses returns compatible secondary tracks recommendations.
- POST /api/v1/profiling/strengths-weaknesses with partial or vague strengths and weaknesses returns a request for clarification or proceeds with limited recommendations.
- StudentStrengthWeakness entity is correctly created or updated with submitted strengths, weaknesses, and partial flag.
- Recommendation logic respects authentication and does not expose unauthorized data.
- Recommendation logic logs inputs and decisions for traceability.

## CLAUDE.md Snippet
### Active Task: Develop recommendation logic for compatible secondary tracks
**Story**: US#9389361 — Academic Strengths and Weaknesses Indication
**Goal**: Provide backend logic to recommend compatible secondary tracks based on student's academic strengths and weaknesses, handling both complete and partial data scenarios.
**Key files**: `backend/api/profiling.py`, `tests/backend/test_profiling_strengths_weaknesses.py`
**Done when**: POST /api/v1/profiling/strengths-weaknesses endpoint returns appropriate recommendations or clarification requests based on submitted academic strengths and weaknesses.
*Delete this section once the task is complete.*
