# Design Bundle

**Locked at:** 2026-07-05 12:08 UTC

## UX Brief

## Screens

### Student Profiling and Exploration
- **Interest Preferences Screen** [Story 9389359]: Entry for 9.º ano students to answer or skip interest questions. Actions: answer interests, skip interests, proceed.
- **Motivations Input Screen** [Story 9389360]: Collect motivations or allow decline. Actions: provide motivations, decline, continue.
- **Academic Strengths and Weaknesses Screen** [Story 9389361]: Input strong/weak disciplines or provide partial info. Actions: submit strengths/weaknesses, clarify, proceed.
- **Profile Summary Screen** [Story 9389363]: View generated profile summary with notes on missing data. Actions: review summary, edit inputs, continue.

### Conversational Guidance Interface
- **Conversational Chat Screen** [Stories 9389364, 9389365, 9389366, 9389368]: Multi-turn chat interface distinguishing facts/interpretations, indicating insufficient info, managing dialogue state, interpreting intent. Actions: ask question, receive answer, follow-up question, change topic.

### Secondary Education Track Analysis
- **Secondary Tracks List Screen** [Story 9389369]: Display all valid secondary tracks with descriptions. Actions: select track, ask about tracks.
- **Track Disciplines Screen** [Story 9389370]: Show disciplines for selected valid track or inform invalid track. Actions: view disciplines, return to tracks.
- **Track Exam Requirements Screen** [Story 9389371]: Show exam requirements and timing for valid track or inform unknown track. Actions: view exams, return.
- **Discipline Combinations Screen** [Story 9389372]: Display valid trienais, bienais, anuais disciplines and combinations or no valid combinations message. Actions: view combinations, return.
- **Track Impact on Higher Ed Screen** [Story 9389373]: Show how track choice affects higher education eligibility or invalid track notice. Actions: view impact, return.

### Higher Education Compatibility Assessment
- **Compatible Courses Screen** [Story 9389374]: List higher education courses compatible with selected secondary track or no data message. Actions: select course, return.
- **Entrance Exam Details Screen** [Story 9389375]: Show required entrance exams and weights for selected course or unavailable info message. Actions: view exams, return.
- **Eligibility Simulation Screen** [Story 9389376]: Simulate eligibility for courses based on secondary track input or incomplete data warning. Actions: input track, view results, correct input.
- **Admission Averages Screen** [Story 9389377]: Display admission averages and exam weights or notify missing data. Actions: select course, view details, return.
- **Compatibility Feedback Screen** [Story 9389378]: Inform no compatible courses found or prompt to correct track input. Actions: edit input, retry.

### Session Memory and State Management
- **Name Input Screen** [Story 9389379]: Prompt for student name with skip option. Actions: enter name, skip.
- **Age Input Screen** [Story 9389380]: Prompt for valid age with validation and retry. Actions: enter age, retry invalid.
- **School Year Input Screen** [Story 9389381]: Select school year within 9.º–12.º range with validation. Actions: select year, retry invalid.
- **Interests Sharing Screen** [Story 9389383]: Input interests or skip for general guidance. Actions: enter interests, skip.
- **Secondary Track Memory Prompt Screen** [Story 9389385]: Prompt to explore track if none explored or confirm stored track. Actions: explore track, ask questions.
- **Session End Screen** [Story 9389387]: Confirm session end and clear stored data. Actions: end session, timeout handling.

### Source-Grounded Retrieval System
- **Document Indexing Status Screen** [Stories 9389382, 9389384, 9389386, 9389388]: Show indexing progress and errors for legal framework, exam guide, secondary-track definitions, higher-ed requirements. Actions: view status, retry indexing.
- **Document Retrieval Screen** [Story 9389389]: Display retrieved official documents supporting answers or no source message. Actions: view sources, ask new question.
- **Answer Fact vs Interpretation Screen** [Story 9389390]: Present answers clearly separating facts and interpretations or indicate lack of basis. Actions: read answer, request clarification.
- **Index Update Screen** [Story 9389391]: Show index update progress or retention message if no updates. Actions: trigger update, view status.

### Human Escalation and Confirmation Paths
- **Confirmation Notification Screen** [Story 9389392]: Alert when question requires human/institutional confirmation. Actions: acknowledge alert, request escalation info.
- **Escalation Instructions Screen** [Story 9389393]: Provide contact details and next steps for confirmation. Actions: view contacts, view instructions.
- **Fact vs Interpretation Marking Screen** [Story 9389394]: Mark answers as fact or interpretation with confirmation advice. Actions: read markings, proceed.
- **Critical Decision Routing Screen** [Story 9389395]: Detect critical decisions and suggest human confirmation, prevent definitive answers. Actions: view suggestion, escalate.

### Family-Focused Explanation Mode
- **Exploration Path Explanation Screen** [Story 9389396]: Show student's interests, motivations, and academic areas in plain language or no data message. Actions: view explanations, close.
- **Guidance Outcomes Explanation Screen** [Story 9389397]: Present guidance recommendations with source-grounded explanations or pending message. Actions: review outcomes, close.
- **Fact and Interpretation Distinction Screen** [Story 9389398]: Clearly separate facts from interpretations in explanations or indicate unavailable info. Actions: read explanations, close.
- **Institutional Confirmation Notification Screen** [Story 9389399]: Alert family about special cases needing institutional confirmation or no alert. Actions: acknowledge alert, close.

## Navigation Paths

- Name Input Screen → Age Input Screen → School Year Input Screen → Interest Preferences Screen → Motivations Input Screen → Academic Strengths and Weaknesses Screen → Profile Summary Screen (Stories: 9389359, 9389360, 9389361, 9389363, 9389379, 9389380, 9389381)

- Conversational Chat Screen → Confirmation Notification Screen → Escalation Instructions Screen (Stories: 9389364, 9389365, 9389366, 9389368, 9389392, 9389393)

- Secondary Tracks List Screen → Track Disciplines Screen → Track Exam Requirements Screen → Discipline Combinations Screen → Track Impact on Higher Ed Screen (Stories: 9389369, 9389370, 9389371, 9389372, 9389373)

- Compatible Courses Screen → Entrance Exam Details Screen → Admission Averages Screen → Eligibility Simulation Screen → Compatibility Feedback Screen (Stories: 9389374, 9389375, 9389376, 9389377, 9389378)

- Exploration Path Explanation Screen → Guidance Outcomes Explanation Screen → Fact and Interpretation Distinction Screen → Institutional Confirmation Notification Screen (Stories: 9389396, 9389397, 9389398, 9389399)

- Document Indexing Status Screen → Document Retrieval Screen → Answer Fact vs Interpretation Screen → Index Update Screen (Stories: 9389382, 9389384, 9389386, 9389388, 9389389, 9389390, 9389391)

### Conversational Guidance Interface
- **Natural Language Question Guidance Screen** [Story 9389362]: Interface to handle natural language questions about secondary tracks, including clarifications and out-of-scope notices. Actions: ask question, receive structured answer, clarify question, receive out-of-scope guidance.

### Navigation Paths
- Conversational Chat Screen → Natural Language Question Guidance Screen → Conversational Chat Screen