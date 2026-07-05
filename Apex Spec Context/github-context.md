# GitHub Repository Context

**Repo:** thomastabs/Possibilista  
**Description:** Possibilista is a conversational, multi-agent school-guidance web application for secondary-school students in Portugal (9.º–12.º ano). It turns open, anxious questions about academic futures into structured, source-grounded guidance: which secondary tracks exist, what disciplines and exams they require, and how those choices open or close doors.  
**Primary language:** Python  
**Default branch:** main  
**Stars:** 0  
**Synced:** 2026-07-05

## File Tree

```
Apex Spec Context/constraints.md
Apex Spec Context/decisions.md
Apex Spec Context/design-bundle.md
Apex Spec Context/figma-context.md
Apex Spec Context/fix-log.md
Apex Spec Context/functional-spec.md
Apex Spec Context/github-context.md
Apex Spec Context/project-concept.md
Apex Spec Context/tech-stack.md
Apex Spec Context/technical-spec.md
DEPENDENCIES.md
Developer Packs/Epic: Student Profiling and Exploration/US#9389359/pack-build-interest-preferences-react-component.md
Developer Packs/Epic: Student Profiling and Exploration/US#9389359/pack-create-studentinterest-entity-and-migration.md
Developer Packs/Epic: Student Profiling and Exploration/US#9389359/pack-implement-post-apiv1profilinginterests-endpoint.md
Developer Packs/Epic: Student Profiling and Exploration/US#9389361/pack-create-studentstrengthweakness-model-and-migration.md
Developer Packs/Epic: Student Profiling and Exploration/US#9389361/pack-implement-post-profilingstrengths-weaknesses-endpoint.md
README.md
apex.md
backend/README.md
backend/__init__.py
backend/api/__init__.py
backend/api/profiling.py
backend/models/__init__.py
backend/models/base.py
backend/models/student_interest.py
backend/models/student_session.py
backend/models/student_strength_weakness.py
backend/requirements.txt
frontend/package.json
migrations/__init__.py
migrations/versions/20260705_01_create_student_interest_table.py
migrations/versions/20260705_02_create_student_strength_weakness_table.py
migrations/versions/__init__.py
src/components/InterestPreferencesScreen.tsx
src/components/__tests__/InterestPreferencesScreen.test.tsx
tests/backend/test_profiling_interests.py
tests/backend/test_profiling_strengths_weaknesses.py
tests/backend/test_student_interest.py
tests/backend/test_student_strength_weakness.py
```

## README

# Possibilista

## Purpose

Possibilista is a conversational, multi-agent school-guidance web application for secondary-school students in Portugal (9.Âºâ12.Âº ano). It turns open, anxious
questions about academic futures into structured, source-grounded guidance: which secondary tracks exist, what disciplines and exams they require, and how
those choices open or close doors to higher-education courses.

The product's governing principle: **the language model is the interface; official
documents are the source of truth.** Every substantive answer is grounded in
official sources via retrieval (RAG), and the assistant explicitly distinguishes
documented fact from interpretation, says when it lacks a basis to answer, and
routes critical decisions to human/institutional confirmation.

## Target Users

- **Students (primary).** Three usage modes by school stage:
  - *Exploration (9.Âº ano):* discover interests, compare secondary areas, understand
    which doors each choice opens or closes.
  - *Management (10.Âºâ12.Âº):* simulate disciplines, exams, averages, and
    compatibility with higher-education courses.
  - *Confirmation (special cases):* identify situations that require institutional
    confirmation (special regimes, equivalences, contingents, specific rules).
- **Families (encarregados de educaÃ§Ã£o).** Secondary audience; need plain-language
  explanations and the ability to follow a student's explored path.
- **Schools.** Future audience for a platform tier with alerts and follow-up.

## Core Value Proposition

- **Accessibility** â first-layer orientation in plain language, available 24/7.
- **Equity** â reduces the advantage held by students with paid/private guidance.
- **Rigour** â answers anchored in official sources, not model recall.
- **Time** â hours of fragmented research compressed into minutes.

It is explicitly a *first* layer of orientation. It does not replace psychologists,
teachers, schools, IAVE/JNE or DGES; it does not guarantee future placements; and
it does not make critical decisions â it structures and informs them.

## System Shape (for downstream design phases)

A coordinated multi-agent system:

- **Orchestrator** â interprets intent, manages conversation state, decides which
  specialists to call, resolves contradictions, assembles the final answer.
- **Profiler agent** â explores interests, motivations, strong/weak disciplines,
  and areas to avoid.
- **Secondary agent (10.Âºâ12.Âº)** â analyses secondary tracks, disciplines, and the
  valid combinations (trienais / bienais / anuais).
- **Superior agent (higher ed)** â cross-references tracks with courses, entrance
  exams (provas de ingresso) and their weights, and entry averages (mÃ©dias).

Supporting concerns: session-only (non-persistent) memory holding name, age, school
year, interests, strong/weak disciplines, goals, explored track and explored
courses; a RAG retrieval layer (chunking â embeddings + vector index â retrieval â
grounded answer with sources); and explicit human-escalation paths.

## MVP Scope

9.Âº-ano exploration + LLM-generated profile + secondary-track exploration + standard
official sources + session memory. Deliberately bounded: out of scope for the MVP are
persistent cross-session memory, API-driven psychometric profiling, and the
school/family platform tier â those are later phases.

## Authoritative Sources (RAG corpus)

- Consolidated legal framework for secondary education.
- General Exam Guide 2026 (calendar, phases, registrations, deadlines).
- Secondary-track definitions (disciplines: trienais, bienais, anuais).
- Higher-education courses (entrance exams and compatibilities).