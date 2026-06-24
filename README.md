# Possibilista

## Purpose

Possibilista is a conversational, multi-agent school-guidance web application for secondary-school students in Portugal (9.º–12.º ano). It turns open, anxious
questions about academic futures into structured, source-grounded guidance: which secondary tracks exist, what disciplines and exams they require, and how
those choices open or close doors to higher-education courses.

The product's governing principle: **the language model is the interface; official
documents are the source of truth.** Every substantive answer is grounded in
official sources via retrieval (RAG), and the assistant explicitly distinguishes
documented fact from interpretation, says when it lacks a basis to answer, and
routes critical decisions to human/institutional confirmation.

## Target Users

- **Students (primary).** Three usage modes by school stage:
  - *Exploration (9.º ano):* discover interests, compare secondary areas, understand
    which doors each choice opens or closes.
  - *Management (10.º–12.º):* simulate disciplines, exams, averages, and
    compatibility with higher-education courses.
  - *Confirmation (special cases):* identify situations that require institutional
    confirmation (special regimes, equivalences, contingents, specific rules).
- **Families (encarregados de educação).** Secondary audience; need plain-language
  explanations and the ability to follow a student's explored path.
- **Schools.** Future audience for a platform tier with alerts and follow-up.

## Core Value Proposition

- **Accessibility** — first-layer orientation in plain language, available 24/7.
- **Equity** — reduces the advantage held by students with paid/private guidance.
- **Rigour** — answers anchored in official sources, not model recall.
- **Time** — hours of fragmented research compressed into minutes.

It is explicitly a *first* layer of orientation. It does not replace psychologists,
teachers, schools, IAVE/JNE or DGES; it does not guarantee future placements; and
it does not make critical decisions — it structures and informs them.

## System Shape (for downstream design phases)

A coordinated multi-agent system:

- **Orchestrator** — interprets intent, manages conversation state, decides which
  specialists to call, resolves contradictions, assembles the final answer.
- **Profiler agent** — explores interests, motivations, strong/weak disciplines,
  and areas to avoid.
- **Secondary agent (10.º–12.º)** — analyses secondary tracks, disciplines, and the
  valid combinations (trienais / bienais / anuais).
- **Superior agent (higher ed)** — cross-references tracks with courses, entrance
  exams (provas de ingresso) and their weights, and entry averages (médias).

Supporting concerns: session-only (non-persistent) memory holding name, age, school
year, interests, strong/weak disciplines, goals, explored track and explored
courses; a RAG retrieval layer (chunking → embeddings + vector index → retrieval →
grounded answer with sources); and explicit human-escalation paths.

## MVP Scope

9.º-ano exploration + LLM-generated profile + secondary-track exploration + standard
official sources + session memory. Deliberately bounded: out of scope for the MVP are
persistent cross-session memory, API-driven psychometric profiling, and the
school/family platform tier — those are later phases.

## Authoritative Sources (RAG corpus)

- Consolidated legal framework for secondary education.
- General Exam Guide 2026 (calendar, phases, registrations, deadlines).
- Secondary-track definitions (disciplines: trienais, bienais, anuais).
- Higher-education courses (entrance exams and compatibilities).
