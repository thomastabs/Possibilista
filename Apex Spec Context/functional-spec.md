# Functional Specification

> Per-story Gherkin Acceptance Criteria.
> Appended automatically by apex after human approval.

## Epic 361769: Student Profiling and Exploration

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

### Story 9389360: Motivations Information Collection

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 11:59 UTC

```gherkin
Feature: Motivations Information Collection

  Scenario: Provide Motivations Successfully
    Given the student is a 9.º ano student
    And the student is ready to provide motivation information
    When the student shares their motivations
    Then the system captures the student's motivations to personalize advice

  Scenario: Decline to Share Motivations
    Given the student is a 9.º ano student
    And the student is presented with motivation questions
    When the student declines to provide motivations
    Then the system continues profiling without motivation data
```

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

### Story 9389363: Profile Summary Generation

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 11:59 UTC

```gherkin
Feature: Profile Summary Generation

  Scenario: Receive Accurate Profile Summary
    Given the student is a 9.º ano student
    And the student has provided inputs about interests, motivations, and academic strengths and weaknesses
    When the student views their profile summary
    Then the system generates a summary based on the student's interests, motivations, and academic strengths and weaknesses

  Scenario: Receive Profile Summary with Missing Data
    Given the student is a 9.º ano student
    And the student has provided incomplete or missing inputs
    When the student views their profile summary
    Then the system generates a summary noting missing or incomplete inputs
    And the system suggests areas to complete for better guidance
```

## Epic 361770: Conversational Guidance Interface

### Story 9389364: Distinguish Facts and Interpretations

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 11:59 UTC

```gherkin
Feature: Distinguish Facts and Interpretations

  Scenario: Receive an answer grounded in official sources
    Given the student asks a question related to official secondary education information
    When the system provides an answer
    Then the answer clearly cites official documents as the source

  Scenario: Receive an interpretative answer
    Given the student asks a question that requires interpretation
    When the system provides an answer including interpretation
    Then the system explicitly states the answer is an interpretation
    And the system clarifies the answer is not a direct quote from official sources
```

### Story 9389365: Indicate Insufficient Information

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 11:59 UTC

```gherkin
Feature: Indicate Insufficient Information

  Scenario: Ask a question with no basis in official documents
    Given the student asks a question with no available official source information
    When the system attempts to answer the question
    Then the system clearly states it cannot answer based on current sources

  Scenario: Ask a question requiring human confirmation
    Given the student asks about a special case or exception
    When the system evaluates the question
    Then the system advises that the question requires confirmation from a human or institution
```

### Story 9389366: Manage Dialogue State

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 11:59 UTC

```gherkin
Feature: Manage Dialogue State

  Scenario: Continue a conversation with related questions
    Given the student is engaged in a multi-turn conversation about secondary education
    When the student asks a follow-up question related to the previous topic
    Then the system remembers the conversation context
    And the system provides a coherent answer based on prior context

  Scenario: Start a new topic mid-conversation
    Given the student is engaged in a multi-turn conversation
    When the student changes the topic abruptly
    Then the system resets the conversation context appropriately
    And the system addresses the new question clearly
```

### Story 9389368: Interpret Student Intent Accurately

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 11:59 UTC

```gherkin
Feature: Interpret Student Intent Accurately

  Scenario: Correctly interpret a straightforward question
    Given the student asks a direct question about secondary education
    When the system processes the question
    Then the system identifies the student's intent accurately
    And the system provides an accurate response

  Scenario: Handle a complex or compound question
    Given the student asks a question involving multiple aspects
    When the system processes the complex question
    Then the system breaks down the intent into parts
    And the system addresses each part clearly
```

### Story 9389362: Natural Language Question Guidance

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 14:36 UTC

```gherkin
Feature: Natural Language Question Guidance

  Scenario: Ask a clear question about secondary tracks
    Given the student is seeking information about secondary education tracks
    When the student asks a clear question about available secondary tracks
    Then the system provides a clear and structured answer
    And the answer references official documents

  Scenario: Ask an ambiguous question
    Given the student is seeking information about secondary education
    When the student asks a vague or ambiguous question
    Then the system requests clarification from the student
    And the system offers options to narrow down the query

  Scenario: Ask a question outside the system's scope
    Given the student is seeking information outside the system's coverage
    When the student asks a question about topics not covered by the system
    Then the system explains it cannot provide an answer
    And the system suggests consulting a human advisor
```

## Epic 361771: Secondary Education Track Analysis

### Story 9389369: Secondary Education Track Information

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 11:59 UTC

```gherkin
Feature: Secondary Education Track Information

  Scenario: List All Available Secondary Tracks
    Given the student is a 9.º ano student
    And the student wants to learn about secondary education tracks
    When the student asks about secondary education tracks
    Then the student receives a list of all valid secondary tracks
    And each track includes a brief description

  Scenario: Ask About A Non-Existent Track
    Given the student is a 9.º ano student
    And the student wants to learn about secondary education tracks
    And the student asks about a secondary track that does not exist
    When the student requests information about the non-existent track
    Then the student is informed that the track is not recognized
    And the student is prompted to ask about valid tracks
```

### Story 9389370: Disciplines Within Secondary Tracks

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 11:59 UTC

```gherkin
Feature: Disciplines Within Secondary Tracks

  Scenario: Request Disciplines For A Valid Track
    Given the student is a 9.º ano student
    And the student wants to learn about disciplines in secondary tracks
    And the student identifies a valid secondary track
    When the student asks which disciplines are included in the valid secondary track
    Then the student receives a detailed list of disciplines included in the track

  Scenario: Request Disciplines For An Invalid Track
    Given the student is a 9.º ano student
    And the student wants to learn about disciplines in secondary tracks
    And the student identifies a secondary track that is not valid
    When the student asks about disciplines for the invalid secondary track
    Then the student is informed that the track is invalid
    And the student is encouraged to ask about valid tracks
```

### Story 9389371: Exam Requirements For Secondary Tracks

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 11:59 UTC

```gherkin
Feature: Exam Requirements For Secondary Tracks

  Scenario: Get Exam Requirements For A Valid Track
    Given the student is a 9.º ano student
    And the student wants to know exam requirements for secondary tracks
    And the student identifies a valid secondary track
    When the student asks about exam requirements for the valid secondary track
    Then the student receives information about required exams for the track
    And the student receives information about the timing of the required exams

  Scenario: Get Exam Requirements For An Unknown Track
    Given the student is a 9.º ano student
    And the student wants to know exam requirements for secondary tracks
    And the student identifies a secondary track not in the official list
    When the student asks about exam requirements for the unknown track
    Then the student is informed that no information is available for that track
```

### Story 9389372: Valid Discipline Combinations

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 11:59 UTC

```gherkin
Feature: Valid Discipline Combinations

  Scenario: Request Valid Discipline Combinations For A Track
    Given the student is a 9.º ano student
    And the student wants to understand valid discipline combinations within a secondary track
    And the student identifies a specific secondary track
    When the student asks about valid discipline combinations for the track
    Then the student receives detailed information about trienais disciplines for the track
    And the student receives detailed information about bienais disciplines for the track
    And the student receives detailed information about anuais disciplines for the track
    And the student receives information about valid combinations of these disciplines

  Scenario: Request Discipline Combinations For A Track With No Valid Combinations
    Given the student is a 9.º ano student
    And the student wants to understand valid discipline combinations within a secondary track
    And the student identifies a secondary track that has no valid discipline combinations
    When the student asks about discipline combinations for the track
    Then the student is informed that there are no valid discipline combinations for the track
```

### Story 9389373: Impact Of Track Choice On Higher Education

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 11:59 UTC

```gherkin
Feature: Impact Of Track Choice On Higher Education

  Scenario: Get Impact Of Track Choice On Higher Education Access
    Given the student is a 9.º ano student
    And the student wants to understand how secondary track choice affects higher education access
    And the student identifies a specific secondary track
    When the student asks how the secondary track influences eligibility for higher education courses
    Then the student receives grounded information linking the track to higher education course requirements

  Scenario: Ask About Impact For An Invalid Track
    Given the student is a 9.º ano student
    And the student wants to understand how secondary track choice affects higher education access
    And the student identifies a secondary track that does not exist
    When the student asks about the impact of the non-existent track on higher education
    Then the student is informed that the track is not recognized
    And the student is informed that no impact information is available for the track
```

## Epic 361772: Higher Education Compatibility Assessment

### Story 9389374: Secondary Track Course Eligibility

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Secondary Track Course Eligibility

  Scenario: Input valid secondary track and receive compatible courses
    Given the student is a 9.º-ano student
    And the student has access to the list of valid secondary tracks
    When the student selects a valid secondary track from the list
    Then the system displays a list of higher education courses compatible with the selected secondary track

  Scenario: Input an invalid or unsupported secondary track
    Given the student is a 9.º-ano student
    And the system has a defined set of recognized secondary tracks
    When the student inputs a secondary track not recognized by the system
    Then the system displays a message indicating no data is available for the entered secondary track
```

### Story 9389375: Entrance Exam Requirements

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Entrance Exam Requirements

  Scenario: View entrance exams for a valid course
    Given the student is a 9.º-ano student
    And the system contains data on higher education courses and their entrance exams
    When the student selects a higher education course present in the system
    Then the system displays the required entrance exams for the selected course
    And the system displays the weight of each required entrance exam

  Scenario: Request entrance exams for a course not in the system
    Given the student is a 9.º-ano student
    And the system has a database of higher education courses
    When the student selects a course not present in the system database
    Then the system informs the student that exam requirements are unavailable for the selected course
```

### Story 9389376: Secondary Track Eligibility Simulation

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Secondary Track Eligibility Simulation

  Scenario: Simulate eligibility with a valid secondary track
    Given the student is a 9.º-ano student
    And the system has official criteria for eligibility based on secondary tracks
    When the student inputs their secondary track
    Then the system displays the higher education courses the student is eligible for based on the official criteria

  Scenario: Simulate eligibility with incomplete or missing track data
    Given the student is a 9.º-ano student
    When the student inputs incomplete or partial secondary track information
    Then the system indicates that eligibility cannot be fully assessed due to incomplete or missing data
```

### Story 9389377: Admission Averages and Exam Weights

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Admission Averages and Exam Weights

  Scenario: View admission averages and exam weights for a course
    Given the student is a 9.º-ano student
    And the system contains admission average and exam weight data for courses
    When the student selects a higher education course
    Then the system displays the required admission average for the selected course
    And the system displays the weight of each entrance exam for the selected course

  Scenario: Request admission criteria for a course with no available data
    Given the student is a 9.º-ano student
    And the system has courses with missing admission average or exam weight data
    When the student selects a course with missing admission average or exam weight data
    Then the system notifies the student that admission criteria information is not available for the selected course
```

### Story 9389378: Feedback on Secondary Track Compatibility

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Feedback on Secondary Track Compatibility

  Scenario: No compatible higher education courses found
    Given the student is a 9.º-ano student
    When the student inputs a secondary track that does not meet any course requirements
    Then the system informs the student that no compatible higher education courses were found

  Scenario: Input invalid or incomplete track data
    Given the student is a 9.º-ano student
    When the student inputs invalid or incomplete secondary track information
    Then the system prompts the student to correct or complete their secondary track input
```

## Epic 361774: Session Memory and State Management

### Story 9389379: Student Name Input

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Student Name Input

  Scenario: Successful name input
    Given the student has started a new session
    When the student provides their name when prompted
    Then the assistant acknowledges the student's name for the session

  Scenario: No name provided
    Given the student has started a new session
    When the student skips entering their name
    Then the assistant continues the conversation without personalization
```

### Story 9389380: Student Age Input

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Student Age Input

  Scenario: Valid age input
    Given the student is in an active session
    When the student provides a valid age
    Then the assistant stores the age for the session

  Scenario: Invalid age input
    Given the student is in an active session
    When the student provides an age outside the valid range
    Then the assistant requests a valid age again
```

### Story 9389381: Student School Year Input

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Student School Year Input

  Scenario: Valid school year input
    Given the student is in an active session
    When the student selects a school year within the 9.º–12.º range
    Then the assistant uses the school year information to guide the conversation

  Scenario: Invalid school year input
    Given the student is in an active session
    When the student inputs a school year outside the 9.º–12.º range
    Then the assistant requests a valid school year
```

### Story 9389383: Student Interests Sharing

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Student Interests Sharing

  Scenario: Interests provided
    Given the student is in an active session
    When the student lists their interests
    Then the assistant stores the interests to tailor exploration

  Scenario: No interests provided
    Given the student is in an active session
    When the student does not provide any interests
    Then the assistant proceeds with general guidance
```

### Story 9389385: Secondary Track Memory

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Secondary Track Memory

  Scenario: Track exploration stored
    Given the student is in an active session
    When the student explores a secondary track
    Then the assistant remembers the explored track for follow-up questions

  Scenario: No track explored yet
    Given the student is in an active session
    When the student asks about secondary tracks without prior exploration
    Then the assistant prompts the student to explore a track first
```

### Story 9389387: Session Memory Reset

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Session Memory Reset

  Scenario: Session ends normally
    Given the student is in an active session with stored data
    When the student ends the session
    Then all stored data is cleared

  Scenario: Session timeout
    Given the student is in an active session with stored data
    When the session times out due to inactivity
    Then all stored data is cleared
```

## Epic 361773: Source-Grounded Retrieval System

### Story 9389382: Legal Framework Document Indexing

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Legal Framework Document Indexing

  Scenario: Successful indexing of legal framework documents
    Given official legal framework documents are available for processing
    When the system processes the legal framework documents
    Then the content of the legal framework documents is searchable for retrieval

  Scenario: Failure to index due to corrupted document format
    Given official legal framework documents include corrupted files
    When the system attempts to process the corrupted legal framework documents
    Then the system detects the corrupted documents
    And the system logs an error
    And the corrupted documents are not indexed
```

### Story 9389384: General Exam Guide Indexing

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: General Exam Guide Indexing

  Scenario: Successful indexing of the General Exam Guide
    Given the General Exam Guide document is available for processing
    When the system processes the General Exam Guide document
    Then the information from the General Exam Guide is included in the searchable index

  Scenario: Failure to index due to missing exam guide document
    Given the General Exam Guide document is missing
    When the system attempts to process the General Exam Guide document
    Then the system identifies the missing document
    And the system alerts the administrator to provide the missing document
```

### Story 9389386: Secondary-Track Definitions Indexing

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Secondary-Track Definitions Indexing

  Scenario: Successful indexing of secondary-track definitions
    Given secondary-track definition documents are available for processing
    When the system processes the secondary-track definition documents
    Then the content of the secondary-track definitions is available for retrieval

  Scenario: Failure to index due to incomplete secondary-track data
    Given secondary-track definition documents are incomplete
    When the system attempts to process the incomplete secondary-track documents
    Then the system detects the incomplete documents
    And the system flags the incomplete documents for review
    And the incomplete documents are not indexed
```

### Story 9389388: Higher-Education Course Requirements Indexing

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Higher-Education Course Requirements Indexing

  Scenario: Successful indexing of higher-education course requirements
    Given documents about higher-education course requirements are available for processing
    When the system processes the higher-education course requirement documents
    Then the higher-education course requirement information is included in the retrieval index

  Scenario: Failure to index due to outdated course requirement documents
    Given higher-education course requirement documents are outdated
    When the system attempts to process the outdated course requirement documents
    Then the system identifies the outdated documents
    And the system prevents the outdated documents from being indexed
    And the system requires updated versions before indexing
```

### Story 9389389: Retrieval of Relevant Official Documents

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Retrieval of Relevant Official Documents

  Scenario: Successful retrieval of relevant documents
    Given the system has indexed official documents
    When the user asks a question within the scope of indexed documents
    Then the system retrieves official documents that directly support the answer

  Scenario: No relevant documents found for a query
    Given the system has indexed official documents
    When the user asks a question outside the scope of indexed documents
    Then the system responds that no official source is available to answer
```

### Story 9389390: Distinguishing Facts and Interpretations in Answers

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Distinguishing Facts and Interpretations in Answers

  Scenario: Answer clearly separates facts from interpretations
    Given the system has access to official sources and interpretation rules
    When the system provides an answer to a user question
    Then the answer explicitly cites official sources for facts
    And any interpretation in the answer is clearly labeled as interpretation

  Scenario: Answer indicates lack of basis for interpretation
    Given the system lacks source information to provide an interpretation
    When the system attempts to provide an interpretation in an answer
    Then the system states it cannot provide an interpretation due to lack of source information
```

### Story 9389391: Index Update on Official Document Changes

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Index Update on Official Document Changes

  Scenario: Successful update of the index after document changes
    Given updated official documents are available
    When the system detects updated official documents
    Then the system refreshes the index to include the updated documents

  Scenario: Failure to update index due to unavailable updated documents
    Given no new versions of official documents are available
    When the system attempts to update the index
    Then the system retains the existing index
```

## Epic 361775: Human Escalation and Confirmation Paths

### Story 9389392: Notification of Confirmation Requirement

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Notification of Confirmation Requirement

  Scenario: System detects ambiguous or critical query
    Given the student is interacting with the system
    And the student asks a question
    When the system identifies the question as ambiguous or critical
    Then the system informs the student that a human or institution must confirm the answer

  Scenario: System cannot find a grounded answer in official sources
    Given the student is interacting with the system
    And the student asks a question outside the scope of official sources
    When the system searches for an answer in official sources
    Then the system states it cannot answer the question
    And the system recommends human or institutional confirmation
```

### Story 9389393: Instructions for Escalation to Confirmation

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Instructions for Escalation to Confirmation

  Scenario: System provides contact details for escalation
    Given the student has been informed that confirmation is needed
    When the system provides information for escalation
    Then the system provides relevant contact information or links to the appropriate human or institutional body

  Scenario: System guides student on next steps for confirmation
    Given the student has been informed that confirmation is needed
    When the system provides guidance on how to proceed with confirmation
    Then the system provides step-by-step instructions including necessary documentation or deadlines
```

### Story 9389394: Distinguishing Facts from Interpretations

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Distinguishing Facts from Interpretations

  Scenario: System clearly marks answers grounded in official sources
    Given the student asks a question
    When the system provides an answer grounded in official sources
    Then the system includes explicit references to official documents
    And the system makes clear the answer is a documented fact

  Scenario: System flags interpretative or uncertain information
    Given the student asks a question
    When the system provides an interpretation or lacks full certainty
    Then the system explicitly states the information is interpretative or uncertain
    And the system advises the student to confirm with a human or institution
```

### Story 9389395: Routing Critical Decisions to Confirmation

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Routing Critical Decisions to Confirmation

  Scenario: System identifies critical decision points
    Given the student is engaged in a conversation involving decisions
    When the student reaches a critical decision point
    Then the system automatically suggests escalation to a human or institution

  Scenario: System prevents providing definitive answers on critical decisions
    Given the student is engaged in a conversation involving a critical decision
    When the system detects the critical decision
    Then the system refrains from giving a definitive answer
    And the system directs the student to seek human confirmation
```

## Epic 361776: Family-Focused Explanation Mode

### Story 9389396: Student Exploration Path Explanation

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Student Exploration Path Explanation

  Scenario: View exploration path with clear simple explanations
    Given the family member is viewing the student's exploration path
    And the explanation mode is available
    When the family member opens the explanation mode
    Then the family member sees the student's interests described in accessible language
    And the family member sees the student's motivations described in accessible language
    And the family member sees the student's explored academic areas described in accessible language

  Scenario: View exploration path when no student data is available
    Given the family member is viewing the student's exploration path
    And the explanation mode is available
    And no exploration path data exists for the student
    When the family member opens the explanation mode
    Then the family member sees a message explaining that the student has not started exploring
```

### Story 9389397: Guidance Outcomes Explanation

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Guidance Outcomes Explanation

  Scenario: View guidance outcomes with source grounded explanations
    Given the family member is viewing the student's guidance outcomes
    And guidance recommendations have been generated
    When the family member reviews the guidance results
    Then each recommendation is accompanied by a plain-language explanation
    And each explanation references official sources

  Scenario: View guidance outcomes when no recommendations are available
    Given the family member is viewing the student's guidance outcomes
    And no guidance recommendations have been generated
    When the family member opens the guidance outcomes section
    Then the family member sees a message indicating that guidance is pending
```

### Story 9389398: Fact and Interpretation Distinction

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Fact and Interpretation Distinction

  Scenario: Explanations clearly separate facts from interpretations
    Given the family member is reading explanations about the student's academic planning
    When the family member reads the explanations
    Then factual information is explicitly identified
    And interpretations or suggestions are clearly marked as such

  Scenario: Explanations indicate when information is unavailable
    Given the family member is reading explanations about the student's academic planning
    When the family member encounters a question or topic without a basis to answer
    Then the system states it lacks a basis to answer
    And the system suggests seeking human or institutional confirmation
```

### Story 9389399: Notifications for Institutional Confirmation

**Status:** Gherkin Locked  
**Locked at:** 2026-07-05 12:00 UTC

```gherkin
Feature: Notifications for Institutional Confirmation

  Scenario: Notification appears for special cases needing confirmation
    Given the family member is viewing the student's explanation mode
    And certain academic choices require confirmation from official institutions
    When the family member views the explanation mode
    Then an alert explains that certain academic choices require confirmation from official institutions

  Scenario: No notification when no special cases are detected
    Given the family member is viewing the student's explanation mode
    And the student's path does not involve special cases requiring confirmation
    When the family member views the explanation mode
    Then no alerts are shown
```