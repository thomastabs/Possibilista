import React, { useMemo, useState } from "react";

type InterestPreferencesScreenProps = {
  bearerToken?: string | null;
  sessionId?: string | null;
  schoolYear?: number | null;
  nextPath?: string;
  onNavigate?: (path: string) => void;
  interestsQuestions?: string[];
};

type ApiResponse = {
  status?: string;
  message?: string;
};

const DEFAULT_INTERESTS = [
  "Technology and programming",
  "Science and experiments",
  "Art and design",
  "Sports and movement",
  "Languages and communication",
  "Business and entrepreneurship",
  "Health and helping others",
  "Music and performance",
];

const MOTIVATIONS_PATH = "/motivations";

export function InterestPreferencesScreen({
  bearerToken,
  sessionId,
  schoolYear,
  nextPath = MOTIVATIONS_PATH,
  onNavigate,
  interestsQuestions = DEFAULT_INTERESTS,
}: InterestPreferencesScreenProps) {
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [customInterest, setCustomInterest] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const isNinthYearStudent = schoolYear === 9;
  const canSubmit = useMemo(() => {
    return !loading && isNinthYearStudent && Boolean(bearerToken);
  }, [bearerToken, isNinthYearStudent, loading]);

  const navigateToNext = () => {
    if (onNavigate) {
      onNavigate(nextPath);
      return;
    }

    if (typeof window !== "undefined") {
      window.location.assign(nextPath);
    }
  };

  const toggleInterest = (interest: string) => {
    setError(null);
    setSuccess(null);
    setSelectedInterests((current) =>
      current.includes(interest)
        ? current.filter((item) => item !== interest)
        : [...current, interest],
    );
  };

  const addCustomInterest = () => {
    const trimmed = customInterest.trim();
    if (!trimmed) {
      return;
    }

    setSelectedInterests((current) =>
      current.includes(trimmed) ? current : [...current, trimmed],
    );
    setCustomInterest("");
  };

  const submitPayload = async (payload: { interests: string[]; skipped: boolean }) => {
    if (!bearerToken) {
      setError("You must be signed in to save interests.");
      return;
    }

    if (!isNinthYearStudent) {
      setError("This screen is only available to 9.º ano students.");
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
      const response = await fetch("/api/v1/session/interests", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${bearerToken}`,
        },
        body: JSON.stringify({ session_id: sessionId, ...payload }),
      });

      const data: ApiResponse = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.message || "Unable to save interest preferences.");
      }

      setSuccess(data.message || "Interest preferences saved.");
      navigateToNext();
    } catch (submitError) {
      const message =
        submitError instanceof Error ? submitError.message : "Unable to save interest preferences.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await submitPayload({ interests: selectedInterests, skipped: false });
  };

  const handleSkip = async () => {
    await submitPayload({ interests: [], skipped: true });
  };

  if (!isNinthYearStudent) {
    return (
      <section aria-labelledby="interest-preferences-title" className="interest-screen">
        <h1 id="interest-preferences-title">Interest preferences</h1>
        <p>This screen is only available to 9.º ano students.</p>
      </section>
    );
  }

  return (
    <section aria-labelledby="interest-preferences-title" className="interest-screen">
      <header className="interest-screen__header">
        <h1 id="interest-preferences-title">Interest preferences</h1>
        <p>Select interests that feel relevant to you, or skip if you want to continue without them.</p>
      </header>

      <form onSubmit={handleSubmit} aria-describedby="interest-preferences-help">
        <p id="interest-preferences-help">
          Your choices help tailor the next guidance step.
        </p>

        <fieldset disabled={loading || !bearerToken} aria-busy={loading}>
          <legend>Suggested interests</legend>
          <div role="list" className="interest-screen__grid">
            {interestsQuestions.map((interest) => {
              const checked = selectedInterests.includes(interest);
              return (
                <label key={interest} className="interest-chip">
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleInterest(interest)}
                    disabled={loading}
                  />
                  <span>{interest}</span>
                </label>
              );
            })}
          </div>
        </fieldset>

        <div className="interest-screen__custom">
          <label htmlFor="custom-interest">Add another interest</label>
          <div className="interest-screen__custom-row">
            <input
              id="custom-interest"
              type="text"
              value={customInterest}
              onChange={(event) => setCustomInterest(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  addCustomInterest();
                }
              }}
              placeholder="Type an interest and press Add"
              disabled={loading || !bearerToken}
            />
            <button
              type="button"
              onClick={addCustomInterest}
              disabled={loading || !bearerToken || !customInterest.trim()}
            >
              Add
            </button>
          </div>
        </div>

        <div aria-live="polite" className="interest-screen__feedback">
          {error ? <p role="alert">{error}</p> : null}
          {success ? <p>{success}</p> : null}
          {!bearerToken ? <p>Sign in to save your answers.</p> : null}
        </div>

        <div className="interest-screen__actions">
          <button type="button" onClick={handleSkip} disabled={loading || !bearerToken}>
            Skip
          </button>
          <button type="submit" disabled={!canSubmit || selectedInterests.length === 0}>
            {loading ? "Saving..." : "Continue"}
          </button>
        </div>
      </form>
    </section>
  );
}

export default InterestPreferencesScreen;
