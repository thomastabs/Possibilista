import React, { useState } from "react";

type SessionAgeResponse = {
  valid?: boolean;
  message?: string;
};

type AgeInputScreenProps = {
  bearerToken?: string | null;
  sessionId?: string | null;
  onContinue?: () => void;
  nextPath?: string;
};

export function AgeInputScreen({
  bearerToken,
  sessionId,
  onContinue,
  nextPath,
}: AgeInputScreenProps) {
  const [age, setAge] = useState<string>("");
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

  const handleAgeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setAge(event.target.value);
    setError(null);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!bearerToken) {
      setError("You must be signed in to continue.");
      return;
    }

    if (!sessionId) {
      setError("A session id is required to continue.");
      return;
    }

    if (!age) {
      setError("Please enter your age.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch("/api/v1/session/age", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${bearerToken}`,
        },
        body: JSON.stringify({ session_id: sessionId, age: Number(age) }),
      });

      const data: SessionAgeResponse = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.message || "Unable to save your age.");
      }

      if (!data.valid) {
        setError(data.message || "Please provide a valid age.");
        return;
      }

      setSuccess(data.message || "Age accepted.");
      navigateToNext();
    } catch (submitError) {
      const message =
        submitError instanceof Error ? submitError.message : "Unable to save your age.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section aria-labelledby="age-input-title" className="age-input-screen">
      <header className="age-input-screen__header">
        <h1 id="age-input-title">How old are you?</h1>
        <p>Enter your age so we can tailor the conversation.</p>
      </header>

      <form onSubmit={handleSubmit} className="age-input-screen__form">
        <label htmlFor="student-age">Your age</label>
        <input
          id="student-age"
          type="number"
          value={age}
          onChange={handleAgeChange}
          placeholder="Enter your age"
          disabled={loading}
        />

        <div className="age-input-screen__actions">
          <button type="submit" disabled={loading || !age}>
            {loading ? "Saving..." : "Continue"}
          </button>
        </div>
      </form>

      <div aria-live="polite" className="age-input-screen__feedback">
        {loading ? <p>Saving...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
        {success ? <p>{success}</p> : null}
      </div>
    </section>
  );
}

export default AgeInputScreen;
