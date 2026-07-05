# Developer Pack — Build Interest Preferences React component
## Story: US#9389359 — Interest Preferences Collection

## Context
Tech stack: LangChain + FastAPI + PostgreSQL + pgvector + React. This task belongs to Story 9389359: Interest Preferences Collection. It involves building the Interest Preferences Screen React component that allows 9.º ano students to answer or skip interest questions. The component must call the POST /api/v1/profiling/interests endpoint to submit interests or skipped flag and handle success or skip flows according to the UX brief.

## Implementation Steps
1. Create a new React component named InterestPreferencesScreen in the frontend React codebase (e.g., src/components/InterestPreferencesScreen.tsx or .jsx).
2. Design the component UI to display a list of interest questions with input controls allowing the student to select or enter multiple interests.
3. Include a 'Skip' button that allows the student to skip answering interest questions.
4. Implement form state management to track selected interests and whether the student chose to skip.
5. On form submission or skip action, call the POST /api/v1/profiling/interests endpoint with the authenticated student's bearer token, sending either the list of interests or skipped=true as per the endpoint contract.
6. Handle the API response by showing success messages or error feedback to the user.
7. Upon successful submission or skip, navigate the user to the next screen in the flow as per the UX navigation path (Motivations Input Screen).
8. Ensure the component handles loading and error states gracefully, including disabling inputs during submission.
9. Validate that only 9.º ano students can access this screen by checking session or user context before rendering or submitting.
10. Add unit and integration tests for the component to verify UI rendering, API calls, and navigation behavior.

## Files to Change
- `src/components/InterestPreferencesScreen.tsx` — Add new React component implementing the Interest Preferences Screen UI and logic, including API integration with POST /api/v1/profiling/interests.

## Test Assertions
- The Interest Preferences Screen React component renders interest questions and allows multiple interests to be selected or entered.
- Submitting interests via the component calls POST /api/v1/profiling/interests with the correct payload and bearer token and handles the response successfully.
- Choosing to skip interest questions calls POST /api/v1/profiling/interests with skipped=true and no interests, and handles the response successfully.
- After successful submission or skip, the component navigates to the Motivations Input Screen as per the UX flow.

## Agentic Brief
**Task**: Build Interest Preferences React component
**Files**: `src/components/InterestPreferencesScreen.tsx`
**Verify**: `npm test -- --testPathPattern=InterestPreferencesScreen`
**Constraints**:
- Use existing frontend React framework and patterns; do not add new dependencies.
- Reuse existing authentication middleware or context to obtain bearer token for API calls.
- Follow UX brief and navigation paths strictly.
- Handle API errors and loading states gracefully in the UI.
- Ensure accessibility and usability for 9.º ano students.
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

**Your Task**: Build Interest Preferences React component
Create the Interest Preferences Screen React component allowing 9.º ano students to answer or skip interest questions. The component should call the POST /api/v1/profiling/interests endpoint to submit the data and handle success or skip flows as per the UX brief.

**Implementation Steps**:
1. Create a new React component named InterestPreferencesScreen in the frontend React codebase (e.g., src/components/InterestPreferencesScreen.tsx or .jsx).
2. Design the component UI to display a list of interest questions with input controls allowing the student to select or enter multiple interests.
3. Include a 'Skip' button that allows the student to skip answering interest questions.
4. Implement form state management to track selected interests and whether the student chose to skip.
5. On form submission or skip action, call the POST /api/v1/profiling/interests endpoint with the authenticated student's bearer token, sending either the list of interests or skipped=true as per the endpoint contract.
6. Handle the API response by showing success messages or error feedback to the user.
7. Upon successful submission or skip, navigate the user to the next screen in the flow as per the UX navigation path (Motivations Input Screen).
8. Ensure the component handles loading and error states gracefully, including disabling inputs during submission.
9. Validate that only 9.º ano students can access this screen by checking session or user context before rendering or submitting.
10. Add unit and integration tests for the component to verify UI rendering, API calls, and navigation behavior.

**Required Test Coverage**:
- The Interest Preferences Screen React component renders interest questions and allows multiple interests to be selected or entered.
- Submitting interests via the component calls POST /api/v1/profiling/interests with the correct payload and bearer token and handles the response successfully.
- Choosing to skip interest questions calls POST /api/v1/profiling/interests with skipped=true and no interests, and handles the response successfully.
- After successful submission or skip, the component navigates to the Motivations Input Screen as per the UX flow.

## CLAUDE.md Snippet
### Active Task: Build Interest Preferences React component
**Story**: US#9389359 — Interest Preferences Collection
**Goal**: Create a React component for the Interest Preferences Screen that submits student interests or skip indication to the backend and integrates into the UX flow.
**Key files**: `src/components/InterestPreferencesScreen.tsx`
**Done when**: The Interest Preferences Screen component submits interests or skip flag to POST /api/v1/profiling/interests and navigates correctly on success.
*Delete this section once the task is complete.*
