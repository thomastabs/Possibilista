import React, { useMemo, useState } from "react";

type AcademicStrengthsWeaknessesScreenProps = {
  bearerToken?: string | null;
  schoolYear?: number | null;
  nextPath?: string;
  onNavigate?: (path: string) => void;
};

type ApiResponse = {
  status?: string;
  message?: string;
};

const DEFAULT_NEXT_PATH = "/profile-summary";

export function AcademicStrengthsWeaknessesScreen({
  bearerToken,
  schoolYear,
  nextPath = DEFAULT_NEXT_PATH,
  onNavigate,
}: AcademicStrengthsWeaknessesScreenProps) {
  const [strengths, setStrengths] = useState<string[]>([]);
  const [weaknesses, setWeaknesses] = useState<string[]>([]);
  const [strengthDraft, setStrengthDraft] = useState("");
  const [weaknessDraft, setWeaknessDraft] = useState("");
  const [partial, setPartial] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const isNinthYearStudent = schoolYear === 9;

  const canSubmit = useMemo(() => {
    if (loading || !bearerToken || !isNinthYearStudent) {
      return false;
    }

    return partial || strengths.length > 0 || weaknesses.length > 0;
  }, [bearerToken, isNinthYearStudent, loading, partial, strengths.length, weaknesses.length]);

  const navigateToNext = () => {
    if (onNavigate) {
      onNavigate(nextPath);
      return;
    }

    if (typeof window !== "undefined") {
      window.location.assign(nextPath);
    }
  };

  const addItem = (
    draft: string,
    setDraft: React.Dispatch<React.SetStateAction<string>>,
    setItems: React.Dispatch<React.SetStateAction<string[]>>,
  ) => {
    const trimmed = draft.trim();
    if (!trimmed) {
      return;
    }

    setError(null);
    setMessage(null);
    setItems((current) => (current.includes(trimmed) ? current : [...current, trimmed]));
    setDraft("");
  };

  const removeItem = (
    value: string,
    setItems: React.Dispatch<React.SetStateAction<string[]>>,
  ) => {
    setError(null);
    setMessage(null);
    setItems((current) => current.filter((item) => item !== value));
  };

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!bearerToken) {
      setError("You must be signed in to save academic strengths and weaknesses.");
      return;
    }

    if (!isNinthYearStudent) {
      setError("This screen is only available to 9.º ano students.");
      return;
    }

    if (!partial && strengths.length === 0 && weaknesses.length === 0) {
      setError("Add at least one strength or weakness, or enable partial input.");
      return;
    }

    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const response = await fetch("/api/v1/profiling/strengths-weaknesses", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${bearerToken}`,
        },
        body: JSON.stringify({ strengths, weaknesses, partial }),
      });

      const data: ApiResponse = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.message || "Unable to save academic strengths and weaknesses.");
      }

      const backendMessage = data.message || "Academic strengths and weaknesses saved.";
      setMessage(backendMessage);

      const needsClarification = backendMessage.toLowerCase().includes("clarification");
      if (!needsClarification) {
        navigateToNext();
      }
    } catch (submitError) {
      const submitMessage =
        submitError instanceof Error
          ? submitError.message
          : "Unable to save academic strengths and weaknesses.";
      setError(submitMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!isNinthYearStudent) {
    return (
      <section aria-labelledby="academic-strengths-title" className="academic-strengths-screen">
        <h1 id="academic-strengths-title">Academic strengths and weaknesses</h1>
        <p>This screen is only available to 9.º ano students.</p>
      </section>
    );
  }

  return (
    <section aria-labelledby="academic-strengths-title" className="academic-strengths-screen">
      <header className="academic-strengths-screen__header">
        <h1 id="academic-strengths-title">Academic strengths and weaknesses</h1>
        <p>
          Add the disciplines you feel confident in and the ones that are harder for you, or
          submit partial information if you want to continue with less detail.
        </p>
      </header>

      <form onSubmit={submit}>
        <div className="academic-strengths-screen__toggle">
          <label>
            <input
              type="checkbox"
              checked={partial}
              onChange={(event) => {
                setPartial(event.target.checked);
                setError(null);
                setMessage(null);
              }}
              disabled={loading}
            />
            Partial information
          </label>
        </div>

        <div className="academic-strengths-screen__group">
          <label htmlFor="strength-draft">Strengths</label>
          <div className="academic-strengths-screen__entry-row">
            <input
              id="strength-draft"
              type="text"
              value={strengthDraft}
              onChange={(event) => setStrengthDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  addItem(strengthDraft, setStrengthDraft, setStrengths);
                }
              }}
              placeholder="Add a discipline"
              disabled={loading}
            />
            <button
              type="button"
              onClick={() => addItem(strengthDraft, setStrengthDraft, setStrengths)}
              disabled={loading || !strengthDraft.trim()}
            >
              Add strength
            </button>
          </div>
          <div className="academic-strengths-screen__chips" aria-label="Selected strengths">
            {strengths.length > 0 ? (
              strengths.map((strength) => (
                <button
                  key={strength}
                  type="button"
                  className="academic-strengths-screen__chip"
                  onClick={() => removeItem(strength, setStrengths)}
                  disabled={loading}
                  aria-label={`Remove strength ${strength}`}
                >
                  {strength}
                </button>
              ))
            ) : (
              <p>No strengths added yet.</p>
            )}
          </div>
        </div>

        <div className="academic-strengths-screen__group">
          <label htmlFor="weakness-draft">Weaknesses</label>
          <div className="academic-strengths-screen__entry-row">
            <input
              id="weakness-draft"
              type="text"
              value={weaknessDraft}
              onChange={(event) => setWeaknessDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  addItem(weaknessDraft, setWeaknessDraft, setWeaknesses);
                }
              }}
              placeholder="Add a discipline"
              disabled={loading}
            />
            <button
              type="button"
              onClick={() => addItem(weaknessDraft, setWeaknessDraft, setWeaknesses)}
              disabled={loading || !weaknessDraft.trim()}
            >
              Add weakness
            </button>
          </div>
          <div className="academic-strengths-screen__chips" aria-label="Selected weaknesses">
            {weaknesses.length > 0 ? (
              weaknesses.map((weakness) => (
                <button
                  key={weakness}
                  type="button"
                  className="academic-strengths-screen__chip"
                  onClick={() => removeItem(weakness, setWeaknesses)}
                  disabled={loading}
                  aria-label={`Remove weakness ${weakness}`}
                >
                  {weakness}
                </button>
              ))
            ) : (
              <p>No weaknesses added yet.</p>
            )}
          </div>
        </div>

        <div aria-live="polite" className="academic-strengths-screen__feedback">
          {error ? <p role="alert">{error}</p> : null}
          {message ? <p>{message}</p> : null}
        </div>

        <div className="academic-strengths-screen__actions">
          <button type="submit" disabled={!canSubmit}>
            {loading ? "Saving..." : "Continue"}
          </button>
        </div>
      </form>
    </section>
  );
}

export default AcademicStrengthsWeaknessesScreen;
