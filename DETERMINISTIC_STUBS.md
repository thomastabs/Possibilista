# Deterministic stubs and missing real implementations

Possibilista's target architecture (`README.md`, `Apex Spec Context/tech-stack.md`) calls for
LangGraph agents doing live RAG retrieval and LLM generation over pgvector. The current repo is a
"thin implementation slice" (per `CLAUDE.md`): every RAG/LLM-shaped surface is instead a
deterministic, rule-based stand-in — no live embedding calls, no live LLM calls — so tests stay
fast and offline, consistent with this repo's testing convention (hand-rolled DB stubs, no real
Postgres connection).

This file tracks every such stub: what it fakes, why, and what swapping in the real thing would
require. Updated as new stories land; not itself a spec document (that's `Apex Spec Context/`).

## Tech stack: LangChain → LangGraph (2026-07-11)

User switched the locked orchestration framework from LangChain to LangGraph in
`Apex Spec Context/tech-stack.md`, `CLAUDE.md`, and `DEPENDENCIES.md`, and swapped
`backend/requirements.txt`'s `langchain==0.2.14` line for `langgraph==0.2.34` (the
`langchain-anthropic`/`langchain-openai`/`langchain-google-genai` model-client packages are
unchanged — LangGraph nodes commonly wrap these same chat model integrations). This was a
pure documentation + dependency-pin change: `grep`ing the backend confirmed nothing anywhere
imports `langchain` or `langgraph` — every RAG/LLM-shaped module in this repo is a stub (see
below), so there was no real orchestration code to migrate.

## backend/services/natural_language_question.py

- **Stubbed**: `retrieve_official_documents` / `_classify_question` — question classification
  (clear/ambiguous/out_of_scope) and document retrieval are plain keyword matching against a
  small hardcoded `_OFFICIAL_DOCUMENT_CATALOG` list, not a vector similarity search.
- **Real implementation would need**: an embedding model call (e.g. via the already-installed
  `langchain-openai`/`langchain-anthropic`/`langchain-google-genai`) to embed the question, a
  pgvector similarity query (`ORDER BY embedding <-> :query_embedding`) against indexed `Document`
  rows, and a LangGraph retrieval graph in place of the keyword classifier.

## backend/services/chat_service.py

- **Stubbed**: `_INTERPRETATION_TERMS` / `_CRITICAL_DECISION_TERMS` / `_contains_any` — fact vs.
  interpretation classification and critical-decision detection are keyword-set membership
  checks, not an LLM judgment call.
- **Real implementation would need**: an LLM call (Orchestrator/Secondary agent per
  `tech-stack.md`) classifying the generated answer's segments as fact-grounded vs. interpretative,
  and a similar LLM-based critical-decision classifier instead of a fixed term list.

## backend/services/embedding_service.py (added US#9389382, extracted for reuse US#9389384, 2026-07-11)

- **Stubbed**: `generate_embedding` — derives a fixed-length numeric vector deterministically from
  content characters (same content always yields the same vector), instead of calling a real
  embedding API. Extracted out of `document_ingestion_service.py` (where it started as a private
  `_generate_embedding`) once a second ingestion pipeline (exam guide) needed the same logic.
- **Real implementation would need**: a real embedding API call (e.g. via the already-installed
  `langchain-openai`/`langchain-anthropic`/`langchain-google-genai`) writing genuine vectors into
  `Document.embedding` (already a real `pgvector.sqlalchemy.Vector` column — only the value
  generation is stubbed).

## backend/services/document_ingestion_service.py (added US#9389382, extended US#9389384/9389386/9389388, 2026-07-11)

- **Stubbed**: `_LEGAL_FRAMEWORK_DOCUMENT_CATALOG` is a small hardcoded list of two valid raw
  candidate documents; `_EXAM_GUIDE_DOCUMENT`, `_SECONDARY_TRACK_DEFINITIONS_CATALOG` (one item),
  and `_HIGHER_ED_REQUIREMENTS_CATALOG` (one item) are each a single hardcoded raw document — all
  four stand in for a real document source (file upload, admin-provided corpus, or external
  legal/exam/admissions-database fetch). "Corrupted"/"missing"/"incomplete"/"outdated" scenarios
  are exercised via explicit test fixtures/parameters (`document=None` for the exam guide;
  hand-written incomplete/outdated documents for the other two) rather than baked into the
  defaults, since the defaults are what the indexing endpoints actually index. Freshness for
  higher-ed requirements is a single hardcoded `HIGHER_ED_REQUIREMENTS_LATEST_VERSION_YEAR = 2026`
  compared against the leading 4-digit year parsed out of `version_label` — not a real "latest
  known version" registry.
- **Real implementation would need**: a real document source (upload endpoint, filesystem watch,
  or external fetch) instead of the static catalog/document, real file-format/content validation
  (e.g. PDF/DOCX parsing with a library like `unstructured` or `pypdf`, and genuine structural
  analysis of parsed sections) instead of the "required fields present" + "content mentions these
  keywords" checks used to detect "corruption"/"missing"/"incomplete" here, and a real version
  registry (e.g. tracking the actual latest published edition per document type) instead of one
  hardcoded expected year.
- **Also note**: `POST /api/v1/documents/index-legal-framework` (US#9389382),
  `POST /api/v1/documents/index-secondary-track-definitions` (US#9389386), and
  `POST /api/v1/documents/index-higher-ed-requirements` (US#9389388) were none of them in the
  locked `Apex Spec Context/technical-spec.md` — that spec maps all three stories only to
  `GET /api/v1/documents/indexing-status`. User chose (2026-07-11, for 9382, applied consistently
  to 9386 and 9388) to amend the spec and add each new endpoint rather than build toward the
  existing `indexing-status` contract instead. Note the inconsistency this leaves: US#9389384's
  exam guide got no dedicated trigger endpoint at all (no pack asked for one) — the other three
  document types each have their own `POST /index-*` endpoint; the generic
  `POST /api/v1/documents/index-update` (Story 9389391, not yet built) is presumably meant to be
  the single trigger eventually, and these four per-type endpoints may end up redundant with it.

## backend/services/indexing_status_service.py (added US#9389384, 2026-07-11)

- **Stubbed**: "administrator alert" for a missing document (Story 9389384's exam guide, and any
  future missing document type) is an ERROR-level log entry plus a synthesized message in
  `GET /api/v1/documents/indexing-status`'s `errors` list — computed live from the absence of
  `Document` rows of that type, not a separately persisted alert record or a real notification
  (email/Slack/etc).
- **Real implementation would need**: a real alerting channel (email, Slack webhook, in-app
  admin notification) triggered when a document type's status flips to `missing`/`failed`,
  instead of relying on an admin polling the status endpoint.

## backend/api/documents.py (added US#9389382, 2026-07-11)

- **Stubbed**: `auth: role:admin` (per the amended spec) is enforced as plain bearer-token
  presence — same as every other endpoint in this repo slice. No role/permission system exists
  anywhere yet to distinguish an admin token from a student-session token.
- **Real implementation would need**: an actual role/claims model on the bearer token (or a
  separate admin auth scheme) and a dependency that rejects non-admin callers, rather than
  `HTTPBearer(auto_error=True)` alone.
