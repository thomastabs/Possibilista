import React, { useState } from "react";

type MotivationsInputScreenProps = {
  bearerToken?: string | null;
  schoolYear?: number | null;
  nextPath?: string;
  onNavigate?: (path: string) => void;
};

type ApiResponse = {
  status?: string;
  message?: string;
};

const DEFAULT_NEXT_PATH = "/academic-strengths-weaknesses";

export function MotivationsInputScreen({
  bearerToken,
  schoolYear,
  nextPath = DEFAULT_NEXT_PATH,
  onNavigate,
}: MotivationsInputScreenProps) {
  const [motivations, setMotivations] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const isNinthYearStudent = schoolYear === 9;

  const navigateToNext = () => {
    if (onNavigate) {
      onNavigate(nextPath);
      return;
    }

    if (typeof window !== "undefined") {
      window.location.assign(nextPath);
    }
  };

  const submitPayload = async (payload: { motivations: string; declined: boolean }) => {
    if (!bearerToken) {
      setError("You must be signed in to save motivations.");
      return;
    }

    if (!isNinthYearStudent) {
      setError("This screen is only available to 9.º ano students.");
      return;
    }

    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const response = await fetch("/api/v1/profiling/motivations", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${bearerToken}`,
        },
        body: JSON.stringify(payload),
      });

      const data: ApiResponse = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.message || "Unable to save motivations.");
      }

      setMessage(data.message || "Motivations saved.");
      navigateToNext();
    } catch (submitError) {
      const submitMessage =
        submitError instanceof Error ? submitError.message : "Unable to save motivations.";
      setError(submitMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmed = motivations.trim();
    if (!trimmed) {
      setError("Enter your motivations or choose to decline.");
      return;
    }

    await submitPayload({ motivations: trimmed, declined: false });
  };

  const handleDecline = async () => {
    await submitPayload({ motivations: "", declined: true });
  };

  if (!isNinthYearStudent) {
    return (
      <section aria-labelledby="motivations-title" className="motivations-screen">
        <h1 id="motivations-title">Motivations</h1>
        <p>This screen is only available to 9.º ano students.</p>
      </section>
    );
  }

  return (
    <section aria-labelledby="motivations-title" className="motivations-screen">
      <header className="motivations-screen__header">
        <h1 id="motivations-title">Motivations</h1>
        <p>
          Share what drives your choices, or skip this step if you prefer not to provide the
          information.
        </p>
      </header>

      <form onSubmit={handleSubmit}>
        <div className="motivations-screen__group">
          <label htmlFor="motivations-input">Your motivations</label>
          <textarea
            id="motivations-input"
            value={motivations}
            onChange={(event) => setMotivations(event.target.value)}
            placeholder="For example: I want to study something creative and practical."
            rows={6}
            disabled={loading}
            aria-describedby="motivations-help"
          />
          <p id="motivations-help">
            This helps personalize the next guidance step.
          </p>
        </div>

        <div aria-live="polite" className="motivations-screen__feedback">
          {error ? <p role="alert">{error}</p> : null}
          {message ? <p>{message}</p> : null}
        </div>

        <div className="motivations-screen__actions">
          <button type="submit" disabled={loading}>
            {loading ? "Saving..." : "Save motivations"}
          </button>
          <button type="button" onClick={handleDecline} disabled={loading}>
            Decline
          </button>
        </div>
      </form>
    </section>
  );
}

export default MotivationsInputScreen;
