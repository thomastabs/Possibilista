# Deterministic stubs and missing real implementations

Possibilista's target architecture (`README.md`, `Apex Spec Context/tech-stack.md`) calls for
LangChain agents doing live RAG retrieval and LLM generation over pgvector. The current repo is a
"thin implementation slice" (per `CLAUDE.md`): every RAG/LLM-shaped surface is instead a
deterministic, rule-based stand-in — no live embedding calls, no live LLM calls — so tests stay
fast and offline, consistent with this repo's testing convention (hand-rolled DB stubs, no real
Postgres connection).

This file tracks every such stub: what it fakes, why, and what swapping in the real thing would
require. Updated as new stories land; not itself a spec document (that's `Apex Spec Context/`).

## backend/services/natural_language_question.py

- **Stubbed**: `retrieve_official_documents` / `_classify_question` — question classification
  (clear/ambiguous/out_of_scope) and document retrieval are plain keyword matching against a
  small hardcoded `_OFFICIAL_DOCUMENT_CATALOG` list, not a vector similarity search.
- **Real implementation would need**: an embedding model call (e.g. via the already-installed
  `langchain-openai`/`langchain-anthropic`/`langchain-google-genai`) to embed the question, a
  pgvector similarity query (`ORDER BY embedding <-> :query_embedding`) against indexed `Document`
  rows, and a LangChain retrieval chain in place of the keyword classifier.

## backend/services/chat_service.py

- **Stubbed**: `_INTERPRETATION_TERMS` / `_CRITICAL_DECISION_TERMS` / `_contains_any` — fact vs.
  interpretation classification and critical-decision detection are keyword-set membership
  checks, not an LLM judgment call.
- **Real implementation would need**: an LLM call (Orchestrator/Secondary agent per
  `tech-stack.md`) classifying the generated answer's segments as fact-grounded vs. interpretative,
  and a similar LLM-based critical-decision classifier instead of a fixed term list.

## backend/services/document_ingestion_service.py (added US#9389382, 2026-07-11)

- **Stubbed**: `_generate_embedding` — derives a fixed-length numeric vector deterministically from
  a document's content characters (same content always yields the same vector), instead of calling
  a real embedding API. `_LEGAL_FRAMEWORK_DOCUMENT_CATALOG` is a small hardcoded list of raw
  candidate documents (one deliberately malformed, to exercise the corrupted-document path) instead
  of a real document source (file upload, admin-provided corpus, or external legal-database fetch).
- **Real implementation would need**: a real embedding call (see above) writing genuine vectors
  into `Document.embedding` (already a real `pgvector.sqlalchemy.Vector` column — only the value
  generation is stubbed), a real document source (upload endpoint, filesystem watch, or external
  fetch) instead of the static catalog, and real file-format validation (e.g. PDF/DOCX parsing
  with a library like `unstructured` or `pypdf`) instead of the "required fields present" check
  used to detect "corruption" here.
- **Also note**: `POST /api/v1/documents/index-legal-framework` was not in the locked
  `Apex Spec Context/technical-spec.md` — that spec maps Story 9389382 only to
  `GET /api/v1/documents/indexing-status`. User chose (2026-07-11) to amend the spec and add the
  new endpoint rather than build toward the existing `indexing-status` contract instead.
