import React, { useState } from "react";

type SessionNameResponse = {
  status?: string;
  message?: string;
};

type StudentNameInputScreenProps = {
  bearerToken?: string | null;
  sessionId?: string | null;
  onContinue?: () => void;
  nextPath?: string;
};

export function StudentNameInputScreen({
  bearerToken,
  sessionId,
  onContinue,
  nextPath,
}: StudentNameInputScreenProps) {
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const navigateToNext = () => {
    if (onContinue) {
      onContinue();
      return;
    }

    if (nextPath && typeof window !== "undefined") {
      window.location.assign(nextPath);
    }
  };

  const submitPayload = async (payload: { name?: string; skipped: boolean }) => {
    if (!bearerToken) {
      setError("You must be signed in to continue.");
      return;
    }

    if (!sessionId) {
      setError("A session id is required to continue.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch("/api/v1/session/name", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${bearerToken}`,
        },
        body: JSON.stringify({ session_id: sessionId, ...payload }),
      });

      const data: SessionNameResponse = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.message || "Unable to save your name.");
      }

      setSuccess(data.message || "Saved.");
      navigateToNext();
    } catch (submitError) {
      const message =
        submitError instanceof Error ? submitError.message : "Unable to save your name.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await submitPayload({ name, skipped: false });
  };

  const handleSkip = async () => {
    await submitPayload({ skipped: true });
  };

  return (
    <section aria-labelledby="student-name-input-title" className="student-name-input-screen">
      <header className="student-name-input-screen__header">
        <h1 id="student-name-input-title">What's your name?</h1>
        <p>Let us know your name so we can personalize your session, or skip if you prefer not to.</p>
      </header>

      <form onSubmit={handleSubmit} className="student-name-input-screen__form">
        <label htmlFor="student-name">Your name</label>
        <input
          id="student-name"
          type="text"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Enter your name"
          disabled={loading}
        />

        <div className="student-name-input-screen__actions">
          <button type="button" onClick={handleSkip} disabled={loading}>
            Skip
          </button>
          <button type="submit" disabled={loading || !name.trim()}>
            {loading ? "Saving..." : "Continue"}
          </button>
        </div>
      </form>

      <div aria-live="polite" className="student-name-input-screen__feedback">
        {loading ? <p>Saving...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
        {success ? <p>{success}</p> : null}
      </div>
    </section>
  );
}

export default StudentNameInputScreen;
