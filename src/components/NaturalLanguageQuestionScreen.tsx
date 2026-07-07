import React, { useState } from "react";

type NaturalLanguageQuestionDocument = {
  title: string;
  content: string;
  source_url: string;
};

type NaturalLanguageQuestionResponse = {
  answer?: string;
  clarification_needed?: boolean;
  clarification_options?: string[];
  out_of_scope?: boolean;
  suggestion?: string;
  session_id?: string;
  documents?: NaturalLanguageQuestionDocument[];
  no_source?: boolean;
};

type NaturalLanguageQuestionScreenProps = {
  bearerToken?: string | null;
  sessionId?: string | null;
};

const DEFAULT_QUESTION =
  "What secondary education tracks are available for a 9.º ano student?";

export function NaturalLanguageQuestionScreen({
  bearerToken,
  sessionId,
}: NaturalLanguageQuestionScreenProps) {
  const [question, setQuestion] = useState(DEFAULT_QUESTION);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<NaturalLanguageQuestionResponse | null>(null);

  const canSubmit = Boolean(bearerToken && sessionId && question.trim() && !loading);

  const submitQuestionText = async (rawQuestion: string) => {
    if (!bearerToken) {
      setError("You must be signed in to ask a question.");
      return;
    }

    if (!sessionId) {
      setError("A session id is required to continue the conversation.");
      return;
    }

    const trimmedQuestion = rawQuestion.trim();
    if (!trimmedQuestion) {
      setError("Enter a question before submitting.");
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const apiResponse = await fetch("/api/v1/chat/natural-language-question", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${bearerToken}`,
        },
        body: JSON.stringify({
          question: trimmedQuestion,
          session_id: sessionId,
        }),
      });

      const data: NaturalLanguageQuestionResponse = await apiResponse.json().catch(() => ({}));

      if (!apiResponse.ok) {
        throw new Error(data.answer || "Unable to process your question.");
      }

      setResponse(data);
    } catch (submitError) {
      const message =
        submitError instanceof Error ? submitError.message : "Unable to process your question.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const submitQuestion = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await submitQuestionText(question);
  };

  const selectClarificationOption = async (option: string) => {
    if (loading) {
      return;
    }
    setQuestion(option);
    await submitQuestionText(option);
  };

  const startNewQuestion = () => {
    setResponse(null);
    setError(null);
    setQuestion("");
  };

  return (
    <section aria-labelledby="natural-language-question-title" className="nlq-screen">
      <header className="nlq-screen__header">
        <h1 id="natural-language-question-title">Natural language question guidance</h1>
        <p>
          Ask about Portuguese secondary education tracks and review answers grounded in official
          documents.
        </p>
      </header>

      <form onSubmit={submitQuestion} className="nlq-screen__form">
        <label htmlFor="natural-language-question">Your question</label>
        <textarea
          id="natural-language-question"
          value={question}
          onChange={(event) => {
            setQuestion(event.target.value);
            setError(null);
          }}
          rows={4}
          placeholder="Type a question about secondary tracks"
          disabled={loading}
        />

        <div className="nlq-screen__actions">
          <button type="submit" disabled={!canSubmit}>
            {loading ? "Asking..." : "Ask question"}
          </button>
        </div>
      </form>

      <div aria-live="polite" className="nlq-screen__feedback">
        {loading ? <p>Loading answer...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
        {!bearerToken ? <p>Sign in to ask a question.</p> : null}
        {!sessionId ? <p>A session id is required to continue the conversation.</p> : null}
      </div>

      {response ? (
        <div className="nlq-screen__response">
          <article className="nlq-screen__answer">
            <h2>Answer</h2>
            <p>{response.answer}</p>
          </article>

          <article className="nlq-screen__facts">
            <h2>Official documents</h2>
            {response.no_source ? (
              <p>No official sources were found for this answer.</p>
            ) : (
              <ul>
                {(response.documents || []).map((document) => (
                  <li key={document.source_url}>
                    <strong>{document.title}</strong>
                    <p>{document.content}</p>
                    <a href={document.source_url} target="_blank" rel="noreferrer">
                      Open source
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </article>

          {response.clarification_needed ? (
            <article className="nlq-screen__clarification">
              <h2>Clarification needed</h2>
              <p>{response.suggestion || "Choose one of the options below."}</p>
              <ul>
                {(response.clarification_options || []).map((option) => (
                  <li key={option}>
                    <button
                      type="button"
                      className="nlq-screen__clarification-option"
                      onClick={() => selectClarificationOption(option)}
                      disabled={loading}
                    >
                      {option}
                    </button>
                  </li>
                ))}
              </ul>
            </article>
          ) : null}

          {response.out_of_scope ? (
            <article className="nlq-screen__out-of-scope" role="alert">
              <h2>Out of scope</h2>
              <p>{response.suggestion}</p>
              <button type="button" onClick={startNewQuestion}>
                Ask a new question
              </button>
            </article>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}

export default NaturalLanguageQuestionScreen;
