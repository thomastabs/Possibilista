"use client";

import { useState } from "react";

import { ConversationalChatScreen } from "@/components/ConversationalChatScreen";
import { DocumentRetrievalScreen } from "@/components/DocumentRetrievalScreen";
import { NaturalLanguageQuestionScreen } from "@/components/NaturalLanguageQuestionScreen";
import { StudentNameInputScreen } from "@/components/StudentNameInputScreen";

export default function PrototypeHomePage() {
  const [sessionId, setSessionId] = useState("");
  const [creatingSession, setCreatingSession] = useState(false);
  const [sessionError, setSessionError] = useState<string | null>(null);

  const trimmedSessionId = sessionId.trim();
  const bearerToken = trimmedSessionId || null;

  const createSession = async () => {
    setCreatingSession(true);
    setSessionError(null);

    try {
      const response = await fetch("/api/v1/session", { method: "POST" });
      const data: { session_id?: string; bearer_token?: string; detail?: string } =
        await response.json().catch(() => ({}));

      if (!response.ok || !data.session_id) {
        throw new Error(data.detail || "Unable to create a prototype session.");
      }

      setSessionId(data.bearer_token || data.session_id);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unable to create a prototype session.";
      setSessionError(message);
    } finally {
      setCreatingSession(false);
    }
  };

  return (
    <main className="prototype-shell">
      <section className="prototype-hero" aria-labelledby="prototype-title">
        <div>
          <p className="prototype-kicker">Possibilista</p>
          <h1 id="prototype-title">Guidance prototype workspace</h1>
          <p>
            Start a prototype session or paste an existing session UUID to exercise the
            deterministic guidance flow.
          </p>
        </div>

        <label className="session-control" htmlFor="session-id">
          <span>Session UUID</span>
          <input
            id="session-id"
            type="text"
            value={sessionId}
            onChange={(event) => setSessionId(event.target.value)}
            placeholder="Paste a student_session id"
          />
          <button type="button" onClick={createSession} disabled={creatingSession}>
            {creatingSession ? "Starting..." : "Start prototype session"}
          </button>
          {sessionError ? <p role="alert">{sessionError}</p> : null}
        </label>
      </section>

      <div className="prototype-grid">
        <StudentNameInputScreen bearerToken={bearerToken} sessionId={trimmedSessionId || null} />
        <ConversationalChatScreen bearerToken={bearerToken} sessionId={trimmedSessionId || null} />
        <NaturalLanguageQuestionScreen bearerToken={bearerToken} sessionId={trimmedSessionId || null} />
        <DocumentRetrievalScreen bearerToken={bearerToken} />
      </div>
    </main>
  );
}
