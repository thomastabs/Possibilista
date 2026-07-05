# Technical Specification

> Project API + data contracts (endpoints + data model).
> Written automatically by apex after human approval.

## Project Design

**Locked at:** 2026-07-05 12:08 UTC

**Stories:** #9389359, #9389360, #9389361, #9389362, #9389363, #9389364, #9389365, #9389366, #9389368, #9389369, #9389370, #9389371, #9389372, #9389373, #9389374, #9389375, #9389376, #9389377, #9389378, #9389379, #9389380, #9389381, #9389382, #9389383, #9389384, #9389385, #9389386, #9389387, #9389388, #9389389, #9389390, #9389391, #9389392, #9389393, #9389394, #9389395, #9389396, #9389397, #9389398, #9389399

### Endpoints

### Student Profiling and Exploration
- `POST /api/v1/profiling/interests` — submit or skip student interest preferences (Story 9389359) · auth: bearer · in: interests:list[str], skipped:bool · out: status:str, message:str
- `POST /api/v1/profiling/motivations` — submit or decline student motivations (Story 9389360) · auth: bearer · in: motivations:str, declined:bool · out: status:str, message:str
- `POST /api/v1/profiling/strengths-weaknesses` — submit academic strengths and weaknesses or partial info (Story 9389361) · auth: bearer · in: strengths:list[str], weaknesses:list[str], partial:bool · out: status:str, message:str
- `GET /api/v1/profiling/summary` — retrieve generated profile summary with notes on missing data (Story 9389363) · auth: bearer · out: profile_summary:str, missing_fields:list[str], suggestions:list[str]

### Conversational Guidance Interface
- `POST /api/v1/chat/message` — send a question and receive an answer distinguishing facts and interpretations, managing dialogue state and intent (Stories 9389364, 9389365, 9389366, 9389368) · auth: bearer · in: message:str, session_id:str · out: answer:str, facts:list[str], interpretations:list[str], insufficient_info:bool, requires_confirmation:bool, session_id:str

### Secondary Education Track Analysis
- `GET /api/v1/secondary-tracks` — list all valid secondary tracks with descriptions (Story 9389369) · auth: none · out: tracks:list[{id:str, name:str, description:str}]
- `GET /api/v1/secondary-tracks/{track_id}/disciplines` — get disciplines for a valid secondary track or invalid notice (Story 9389370) · auth: none · out: valid:bool, disciplines:list[str], message:str
- `GET /api/v1/secondary-tracks/{track_id}/exam-requirements` — get exam requirements and timing for a valid track or unknown track notice (Story 9389371) · auth: none · out: valid:bool, exams:list[{name:str, timing:str}], message:str
- `GET /api/v1/secondary-tracks/{track_id}/discipline-combinations` — get valid trienais, bienais, anuais disciplines and combinations or no valid combinations message (Story 9389372) · auth: none · out: valid:bool, trienais:list[str], bienais:list[str], anuais:list[str], combinations:list[str], message:str
- `GET /api/v1/secondary-tracks/{track_id}/higher-ed-impact` — get impact of track choice on higher education eligibility or invalid track notice (Story 9389373) · auth: none · out: valid:bool, impact_description:str, message:str

### Higher Education Compatibility Assessment
- `GET /api/v1/higher-ed/courses` — list higher education courses compatible with selected secondary track or no data message (Story 9389374) · auth: none · in: secondary_track_id:str · out: courses:list[{id:str, name:str}], message:str
- `GET /api/v1/higher-ed/courses/{course_id}/entrance-exams` — get required entrance exams and weights for selected course or unavailable info message (Story 9389375) · auth: none · out: available:bool, exams:list[{name:str, weight:float}], message:str
- `POST /api/v1/higher-ed/eligibility-simulation` — simulate eligibility for courses based on secondary track input or incomplete data warning (Story 9389376) · auth: none · in: secondary_track_id:str · out: eligible_courses:list[{id:str, name:str}], incomplete_data:bool, message:str
- `GET /api/v1/higher-ed/courses/{course_id}/admission-averages` — get admission averages and exam weights or notify missing data (Story 9389377) · auth: none · out: available:bool, admission_average:float, exam_weights:list[{exam_name:str, weight:float}], message:str
- `POST /api/v1/higher-ed/compatibility-feedback` — provide feedback on secondary track compatibility or prompt to correct input (Story 9389378) · auth: none · in: secondary_track_id:str · out: compatible:bool, message:str

### Session Memory and State Management
- `POST /api/v1/session/name` — input student name or skip (Story 9389379) · auth: bearer · in: name:str, skipped:bool · out: status:str, message:str
- `POST /api/v1/session/age` — input valid age with validation and retry (Story 9389380) · auth: bearer · in: age:int · out: valid:bool, message:str
- `POST /api/v1/session/school-year` — select school year within 9.º–12.º range with validation (Story 9389381) · auth: bearer · in: school_year:int · out: valid:bool, message:str
- `POST /api/v1/session/interests` — input interests or skip for general guidance (Story 9389383) · auth: bearer · in: interests:list[str], skipped:bool · out: status:str, message:str
- `GET /api/v1/session/secondary-track-memory` — prompt to explore track if none explored or confirm stored track (Story 9389385) · auth: bearer · out: track_explored:bool, stored_track_id:str, message:str
- `POST /api/v1/session/end` — confirm session end and clear stored data (Story 9389387) · auth: bearer · out: status:str, message:str

### Source-Grounded Retrieval System
- `GET /api/v1/documents/indexing-status` — show indexing progress and errors for all document types (Stories 9389382, 9389384, 9389386, 9389388) · auth: role:admin · out: legal_framework_status:str, exam_guide_status:str, secondary_track_definitions_status:str, higher_ed_requirements_status:str, errors:list[str]
- `GET /api/v1/documents/retrieve` — retrieve official documents supporting answers or no source message (Story 9389389) · auth: bearer · in: query:str · out: documents:list[{title:str, content:str, source_url:str}], no_source:bool
- `GET /api/v1/answers/fact-interpretation` — present answers separating facts and interpretations or indicate lack of basis (Story 9389390) · auth: bearer · in: answer_id:str · out: facts:list[str], interpretations:list[str], no_basis:bool
- `POST /api/v1/documents/index-update` — trigger index update and show progress or retention message (Story 9389391) · auth: role:admin · out: updated:bool, message:str

### Human Escalation and Confirmation Paths
- `GET /api/v1/escalation/confirmation-notification` — alert when question requires human/institutional confirmation (Story 9389392) · auth: bearer · in: question:str · out: requires_confirmation:bool, message:str
- `GET /api/v1/escalation/instructions` — provide contact details and next steps for confirmation (Story 9389393) · auth: bearer · out: contacts:list[{name:str, phone:str, email:str}], instructions:str
- `GET /api/v1/answers/fact-interpretation-marking` — mark answers as fact or interpretation with confirmation advice (Story 9389394) · auth: bearer · in: answer_id:str · out: is_fact:bool, is_interpretation:bool, confirmation_advice:str
- `GET /api/v1/escalation/critical-decision-routing` — detect critical decisions and suggest human confirmation, prevent definitive answers (Story 9389395) · auth: bearer · in: conversation_context:str · out: critical_decision_detected:bool, suggestion:str

### Family-Focused Explanation Mode
- `GET /api/v1/family/exploration-path` — show student's interests, motivations, academic areas in plain language or no data message (Story 9389396) · auth: bearer · in: student_session_id:str · out: interests_explanation:str, motivations_explanation:str, academic_areas_explanation:str, no_data:bool
- `GET /api/v1/family/guidance-outcomes` — present guidance recommendations with source-grounded explanations or pending message (Story 9389397) · auth: bearer · in: student_session_id:str · out: recommendations:list[{text:str, source:str}], pending:bool
- `GET /api/v1/family/fact-interpretation-distinction` — separate facts from interpretations in explanations or indicate unavailable info (Story 9389398) · auth: bearer · in: explanation_id:str · out: facts:list[str], interpretations:list[str], unavailable_info:bool
- `GET /api/v1/family/institutional-confirmation-notification` — alert family about special cases needing institutional confirmation or no alert (Story 9389399) · auth: bearer · in: student_session_id:str · out: alert_present:bool, alert_message:str

### Conversational Guidance Interface
- POST /api/v1/chat/natural-language-question — handle natural language questions about secondary tracks, request clarifications, or provide out-of-scope notices (Story 9389362) · auth: bearer · in: question:str, session_id:str · out: answer:str, clarification_needed:bool, clarification_options:list[str], out_of_scope:bool, suggestion:str, session_id:str

### Data Model

## Data Model

### StudentSession
- Fields: session_id: str, student_name: str (nullable), age: int (nullable), school_year: int (nullable), track_explored: bool, stored_track_id: str (nullable)
- Relations: has many StudentInterest, has one StudentMotivation, has one StudentStrengthWeakness, has many ChatMessage, has many SessionSecondaryTrackMemory

### StudentInterest
- Fields: id: str, session_id: str, interest: str, skipped: bool
- Relations: belongs to StudentSession

### StudentMotivation
- Fields: id: str, session_id: str, motivations: str, declined: bool
- Relations: belongs to StudentSession

### StudentStrengthWeakness
- Fields: id: str, session_id: str, strengths: list[str], weaknesses: list[str], partial: bool
- Relations: belongs to StudentSession

### ChatMessage
- Fields: id: str, session_id: str, message: str, answer: str, facts: list[str], interpretations: list[str], insufficient_info: bool, requires_confirmation: bool, timestamp: datetime
- Relations: belongs to StudentSession

### SecondaryTrack
- Fields: id: str, name: str, description: str
- Relations: has many SecondaryTrackDiscipline, has many SecondaryTrackExamRequirement, has one SecondaryTrackDisciplineCombination, has one SecondaryTrackHigherEdImpact, has many HigherEdCourseCompatibility

### SecondaryTrackDiscipline
- Fields: id: str, track_id: str, discipline_name: str
- Relations: belongs to SecondaryTrack

### SecondaryTrackExamRequirement
- Fields: id: str, track_id: str, exam_name: str, timing: str
- Relations: belongs to SecondaryTrack

### SecondaryTrackDisciplineCombination
- Fields: id: str, track_id: str, trienais: list[str], bienais: list[str], anuais: list[str], combinations: list[str], message: str
- Relations: belongs to SecondaryTrack

### SecondaryTrackHigherEdImpact
- Fields: id: str, track_id: str, impact_description: str, message: str
- Relations: belongs to SecondaryTrack

### HigherEdCourse
- Fields: id: str, name: str
- Relations: has many HigherEdCourseEntranceExam, has one HigherEdCourseAdmissionAverage, has many HigherEdCourseCompatibility

### HigherEdCourseEntranceExam
- Fields: id: str, course_id: str, exam_name: str, weight: float
- Relations: belongs to HigherEdCourse

### HigherEdCourseAdmissionAverage
- Fields: id: str, course_id: str, admission_average: float, exam_weights: list[{exam_name: str, weight: float}], message: str
- Relations: belongs to HigherEdCourse

### HigherEdCourseCompatibility
- Fields: id: str, course_id: str, secondary_track_id: str, compatible: bool, message: str
- Relations: belongs to HigherEdCourse, belongs to SecondaryTrack

### EligibilitySimulationResult
- Fields: id: str, secondary_track_id: str, eligible_courses: list[{id: str, name: str}], incomplete_data: bool, message: str
- Relations: belongs to SecondaryTrack

### Document
- Fields: id: str, title: str, content: str, source_url: str, document_type: str, version_label: str, indexed: bool, indexing_errors: list[str]
- Relations: none

### Explanation
- Fields: id: str, explanation_id: str, facts: list[str], interpretations: list[str], unavailable_info: bool
- Relations: none

### EscalationContact
- Fields: id: str, name: str, phone: str, email: str, instructions: str
- Relations: none