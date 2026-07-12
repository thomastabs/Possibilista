import React, { useState } from "react";

type SchoolYearResponse = {
  valid?: boolean;
  message?: string;
};

type SchoolYearInputScreenProps = {
  bearerToken?: string | null;
  sessionId?: string | null;
  onContinue?: () => void;
  nextPath?: string;
};

const SCHOOL_YEAR_OPTIONS = [9, 10, 11, 12];

export function SchoolYearInputScreen({
  bearerToken,
  sessionId,
  onContinue,
  nextPath,
}: SchoolYearInputScreenProps) {
  const [schoolYear, setSchoolYear] = useState<string>("");
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

    if (!schoolYear) {
      setError("Please select your school year.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch("/api/v1/session/school-year", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${bearerToken}`,
        },
        body: JSON.stringify({ session_id: sessionId, school_year: Number(schoolYear) }),
      });

      const data: SchoolYearResponse = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.message || "Unable to save your school year.");
      }

      if (!data.valid) {
        setError(data.message || "Please provide a valid school year.");
        return;
      }

      setSuccess(data.message || "School year accepted.");
      navigateToNext();
    } catch (submitError) {
      const message =
        submitError instanceof Error ? submitError.message : "Unable to save your school year.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section aria-labelledby="school-year-input-title" className="school-year-input-screen">
      <header className="school-year-input-screen__header">
        <h1 id="school-year-input-title">What's your school year?</h1>
        <p>Select your school year (9.º to 12.º) so we can tailor the conversation.</p>
      </header>

      <form onSubmit={handleSubmit} className="school-year-input-screen__form">
        <label htmlFor="school-year">School year</label>
        <select
          id="school-year"
          value={schoolYear}
          onChange={(event) => setSchoolYear(event.target.value)}
          disabled={loading}
        >
          <option value="">Select a school year</option>
          {SCHOOL_YEAR_OPTIONS.map((year) => (
            <option key={year} value={year}>
              {year}.º ano
            </option>
          ))}
        </select>

        <div className="school-year-input-screen__actions">
          <button type="submit" disabled={loading || !schoolYear}>
            {loading ? "Saving..." : "Continue"}
          </button>
        </div>
      </form>

      <div aria-live="polite" className="school-year-input-screen__feedback">
        {loading ? <p>Saving...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
        {success ? <p>{success}</p> : null}
      </div>
    </section>
  );
}

export default SchoolYearInputScreen;
