# Constraints

EARS-structured quality constraints for the whole project. Behavioural requirements live in the Gherkin acceptance criteria.

## Availability

- **NFR-4** _(ubiquitous)_: The Possibilista system shall maintain 24/7 availability to provide continuous accessibility to students and families.
  - _Rationale:_ Accessibility is a core value proposition requiring high availability.
- **NFR-13** _(unwanted-behaviour)_: If the PostgreSQL database becomes unavailable, then the system shall degrade gracefully by notifying users and disabling retrieval-dependent features.
  - _Rationale:_ Graceful degradation maintains user awareness and system stability during outages.

## Compliance

- **NFR-9** _(ubiquitous)_: The Possibilista system shall comply with applicable data protection regulations for handling student personal data in Portugal.
  - _Rationale:_ Compliance with legal frameworks is mandatory for handling personal data.

## Maintainability

- **NFR-6** _(ubiquitous)_: The system shall centralize LangChain agent chains and RAG pipelines in a single codebase to facilitate maintainability and reduce complexity.
  - _Rationale:_ A unified codebase simplifies development and maintenance.

## Observability

- **NFR-7** _(ubiquitous)_: The Possibilista system shall log retrieval queries and agent decisions to enable traceability of answers grounded in official sources.
  - _Rationale:_ Observability supports rigour by allowing audit of source-grounded responses.

## Performance

- **NFR-2** _(event-driven)_: When multiple concurrent chat sessions occur, the FastAPI backend shall respond to conversational agent requests within 500ms under low-to-medium load (target 	60ms).
  - _Rationale:_ FastAPI async support must handle concurrent chat sessions with acceptable latency for usability.
- **NFR-12** _(ubiquitous)_: The RAG retrieval layer using pgvector shall return relevant official documents within 300ms to support responsive answer generation (target 	30ms).
  - _Rationale:_ Fast retrieval is essential for conversational responsiveness and user experience.

## Reliability

- **NFR-3** _(unwanted-behaviour)_: If the document ingestion pipeline processes large uploads, then the system shall prevent request timeouts by limiting ingestion duration or offloading ingestion tasks.
  - _Rationale:_ In-process ingestion risks request timeouts that would degrade system reliability.
- **NFR-11** _(ubiquitous)_: The system shall indicate when insufficient information exists to answer a query rather than generating unsupported responses.
  - _Rationale:_ Reliability demands honest communication about knowledge limits to avoid misinformation.

## Scalability

- **NFR-5** _(unwanted-behaviour)_: If simulation request volume spikes, then the system shall prevent starvation of conversational agents by managing resource allocation or request prioritization.
  - _Rationale:_ Shared process architecture risks resource contention affecting responsiveness.

## Security

- **NFR-1** _(ubiquitous)_: The Possibilista system shall enforce secure access controls to protect student session data and prevent unauthorized access.
  - _Rationale:_ Protecting sensitive student information is critical given the personal profiling and session memory stored in PostgreSQL.
- **NFR-8** _(ubiquitous)_: The system shall encrypt sensitive data at rest in PostgreSQL, including session memory and user profiles.
  - _Rationale:_ Encryption protects sensitive student data stored in the database.

## Usability

- **NFR-10** _(ubiquitous)_: The conversational interface shall clearly distinguish between documented facts and model interpretations in all responses.
  - _Rationale:_ Usability requires transparency to build user trust and align with the governing principle.