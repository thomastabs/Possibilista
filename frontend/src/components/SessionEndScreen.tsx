import React, { useState } from "react";

type SessionEndResponse = {
  status?: string;
  message?: string;
};

type SessionEndScreenProps = {
  bearerToken?: string | null;
  sessionId?: string | null;
  onSessionEnded?: () => void;
  onCancel?: () => void;
};

export function SessionEndScreen({
  bearerToken,
  sessionId,
  onSessionEnded,
  onCancel,
}: SessionEndScreenProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ended, setEnded] = useState(false);
  const [message, setMessage] = useState<string>("");

  const handleConfirm = async () => {
    if (!bearerToken) {
      setError("You must be signed in to end the session.");
      return;
    }

    if (!sessionId) {
      setError("A session id is required to end the session.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/v1/session/end", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${bearerToken}`,
        },
        body: JSON.stringify({ session_id: sessionId }),
      });

      const data: SessionEndResponse = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.message || "Unable to end the session.");
      }

      setEnded(true);
      setMessage(data.message || "Session data was cleared.");
      onSessionEnded?.();
    } catch (submitError) {
      const errorMessage =
        submitError instanceof Error ? submitError.message : "Unable to end the session.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section aria-labelledby="session-end-title" className="session-end-screen">
      <h1 id="session-end-title">End session</h1>

      {!ended ? (
        <div className="session-end-screen__confirm">
          <p>Are you sure you want to end this session? All stored data will be cleared.</p>
          <div className="session-end-screen__actions">
            <button type="button" onClick={onCancel} disabled={loading}>
              Cancel
            </button>
            <button type="button" onClick={handleConfirm} disabled={loading}>
              {loading ? "Ending..." : "Confirm"}
            </button>
          </div>
        </div>
      ) : null}

      <div aria-live="polite" className="session-end-screen__feedback">
        {error ? <p role="alert">{error}</p> : null}
        {ended ? <p role="status">{message}</p> : null}
      </div>
    </section>
  );
}

export default SessionEndScreen;
