import React, { useState } from "react";

type ChatTurn = {
  id: string;
  question: string;
  answer: string;
  facts: string[];
  interpretations: string[];
  insufficient_info: boolean;
  requires_confirmation: boolean;
};

type ChatMessageResponse = {
  answer?: string;
  facts?: string[];
  interpretations?: string[];
  insufficient_info?: boolean;
  requires_confirmation?: boolean;
  session_id?: string;
};

type ConversationalChatScreenProps = {
  bearerToken?: string | null;
  sessionId?: string | null;
};

let turnIdCounter = 0;

function nextTurnId(): string {
  turnIdCounter += 1;
  return `turn-${turnIdCounter}`;
}

export function ConversationalChatScreen({
  bearerToken,
  sessionId,
}: ConversationalChatScreenProps) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);
  const [history, setHistory] = useState<ChatTurn[]>([]);

  const canSubmit = Boolean(bearerToken && sessionId && message.trim() && !loading);

  const sendMessage = async (rawMessage: string) => {
    if (!bearerToken) {
      setError("You must be signed in to send a message.");
      return;
    }

    if (!sessionId) {
      setError("A session id is required to continue the conversation.");
      return;
    }

    const trimmedMessage = rawMessage.trim();
    if (!trimmedMessage) {
      setError("Enter a message before submitting.");
      return;
    }

    setLoading(true);
    setError(null);
    setPendingMessage(trimmedMessage);

    try {
      const apiResponse = await fetch("/api/v1/chat/message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${bearerToken}`,
        },
        body: JSON.stringify({
          message: trimmedMessage,
          session_id: sessionId,
        }),
      });

      const data: ChatMessageResponse = await apiResponse.json().catch(() => ({}));

      if (!apiResponse.ok) {
        throw new Error(data.answer || "Unable to send your message.");
      }

      setHistory((previous) => [
        ...previous,
        {
          id: nextTurnId(),
          question: trimmedMessage,
          answer: data.answer || "",
          facts: data.facts || [],
          interpretations: data.interpretations || [],
          insufficient_info: Boolean(data.insufficient_info),
          requires_confirmation: Boolean(data.requires_confirmation),
        },
      ]);
      setPendingMessage(null);
      setMessage("");
    } catch (submitError) {
      const messageText =
        submitError instanceof Error ? submitError.message : "Unable to send your message.";
      setError(messageText);
    } finally {
      setLoading(false);
    }
  };

  const submitMessage = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await sendMessage(message);
  };

  const retryPendingMessage = async () => {
    if (pendingMessage) {
      await sendMessage(pendingMessage);
    }
  };

  return (
    <section aria-labelledby="conversational-chat-title" className="chat-screen">
      <header className="chat-screen__header">
        <h1 id="conversational-chat-title">Conversational guidance chat</h1>
        <p>
          Ask questions across the conversation. Each answer clearly separates documented
          facts from interpretation.
        </p>
      </header>

      <ol className="chat-screen__history">
        {history.map((turn) => (
          <li key={turn.id} className="chat-screen__turn">
            <p className="chat-screen__question">
              <strong>You:</strong> <span>{turn.question}</span>
            </p>

            <div className="chat-screen__answer">
              <p>{turn.answer}</p>

              {turn.requires_confirmation ? (
                <p role="alert" className="chat-screen__confirmation-alert">
                  Human or institutional confirmation is recommended for this answer.
                </p>
              ) : null}

              {turn.insufficient_info ? (
                <p role="status" className="chat-screen__insufficient-info">
                  The system cannot answer this question based on the current official sources.
                </p>
              ) : null}

              {turn.facts.length > 0 ? (
                <article className="chat-screen__facts">
                  <h2>Facts</h2>
                  <ul>
                    {turn.facts.map((fact) => (
                      <li key={fact}>{fact}</li>
                    ))}
                  </ul>
                </article>
              ) : null}

              {turn.interpretations.length > 0 ? (
                <article className="chat-screen__interpretations">
                  <h2>Interpretation</h2>
                  <ul>
                    {turn.interpretations.map((interpretation) => (
                      <li key={interpretation}>{interpretation}</li>
                    ))}
                  </ul>
                </article>
              ) : null}
            </div>
          </li>
        ))}
      </ol>

      <form onSubmit={submitMessage} className="chat-screen__form">
        <label htmlFor="conversational-chat-message">Your message</label>
        <textarea
          id="conversational-chat-message"
          value={message}
          onChange={(event) => {
            setMessage(event.target.value);
            setError(null);
          }}
          rows={3}
          placeholder="Ask a question about secondary tracks"
          disabled={loading}
        />

        <div className="chat-screen__actions">
          <button type="submit" disabled={!canSubmit}>
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
      </form>

      <div aria-live="polite" className="chat-screen__feedback">
        {loading ? <p>Waiting for a response...</p> : null}
        {error ? (
          <div className="chat-screen__error">
            <p role="alert">{error}</p>
            {pendingMessage ? (
              <button type="button" onClick={retryPendingMessage} disabled={loading}>
                Retry
              </button>
            ) : null}
          </div>
        ) : null}
        {!bearerToken ? <p>Sign in to start the conversation.</p> : null}
        {!sessionId ? <p>A session id is required to continue the conversation.</p> : null}
      </div>
    </section>
  );
}

export default ConversationalChatScreen;
