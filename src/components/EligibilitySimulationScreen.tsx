import React, { useEffect, useState } from "react";

type SecondaryTrackOption = {
  id: string;
  name: string;
  description?: string | null;
};

type SecondaryTracksResponse = {
  tracks: SecondaryTrackOption[];
};

type HigherEdCourse = {
  id: string;
  name: string;
};

type EligibilitySimulationResponse = {
  eligible_courses: HigherEdCourse[];
  incomplete_data: boolean;
  message: string;
};

type EligibilitySimulationScreenProps = {
  bearerToken?: string | null;
  onBack?: () => void;
  onContinue?: () => void;
};

export function EligibilitySimulationScreen({
  bearerToken,
  onBack,
  onContinue,
}: EligibilitySimulationScreenProps) {
  const [tracks, setTracks] = useState<SecondaryTrackOption[]>([]);
  const [selectedTrackId, setSelectedTrackId] = useState<string>("");
  const [tracksLoading, setTracksLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [incompleteData, setIncompleteData] = useState<boolean | null>(null);
  const [eligibleCourses, setEligibleCourses] = useState<HigherEdCourse[]>([]);
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    const fetchTracks = async () => {
      setTracksLoading(true);

      try {
        const headers: Record<string, string> = {};
        if (bearerToken) {
          headers.Authorization = `Bearer ${bearerToken}`;
        }

        const apiResponse = await fetch("/api/v1/secondary-tracks", { headers });
        const data: SecondaryTracksResponse = await apiResponse
          .json()
          .catch(() => ({ tracks: [] }));

        if (cancelled) {
          return;
        }

        setTracks(data.tracks || []);
      } catch {
        if (!cancelled) {
          setTracks([]);
        }
      } finally {
        if (!cancelled) {
          setTracksLoading(false);
        }
      }
    };

    fetchTracks();

    return () => {
      cancelled = true;
    };
  }, [bearerToken]);

  const submitSimulation = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!selectedTrackId) {
      setError("Select a secondary track before simulating eligibility.");
      return;
    }

    setSubmitting(true);
    setError(null);
    setIncompleteData(null);
    setEligibleCourses([]);
    setMessage("");

    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (bearerToken) {
        headers.Authorization = `Bearer ${bearerToken}`;
      }

      const apiResponse = await fetch("/api/v1/higher-ed/eligibility-simulation", {
        method: "POST",
        headers,
        body: JSON.stringify({ secondary_track_id: selectedTrackId }),
      });

      const data: EligibilitySimulationResponse = await apiResponse
        .json()
        .catch(() => ({ eligible_courses: [], incomplete_data: false, message: "" }));

      if (!apiResponse.ok) {
        throw new Error(data.message || "Unable to simulate eligibility for this track.");
      }

      setIncompleteData(data.incomplete_data);
      setEligibleCourses(data.eligible_courses || []);
      setMessage(data.message || "");
    } catch (submitError) {
      const errorMessage =
        submitError instanceof Error
          ? submitError.message
          : "Unable to simulate eligibility for this track.";
      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section
      aria-labelledby="eligibility-simulation-title"
      className="eligibility-simulation-screen"
    >
      <header className="eligibility-simulation-screen__header">
        <h1 id="eligibility-simulation-title">Eligibility simulation</h1>
        <button type="button" onClick={onBack}>
          Back
        </button>
      </header>

      <form onSubmit={submitSimulation} className="eligibility-simulation-screen__form">
        <label htmlFor="eligibility-simulation-track">Secondary track</label>
        <select
          id="eligibility-simulation-track"
          value={selectedTrackId}
          onChange={(event) => setSelectedTrackId(event.target.value)}
          disabled={tracksLoading || submitting}
        >
          <option value="">Select a secondary track</option>
          {tracks.map((track) => (
            <option key={track.id} value={track.id}>
              {track.name}
            </option>
          ))}
        </select>

        <div className="eligibility-simulation-screen__actions">
          <button type="submit" disabled={submitting || tracksLoading}>
            {submitting ? "Simulating..." : "Simulate eligibility"}
          </button>
        </div>
      </form>

      <div aria-live="polite" className="eligibility-simulation-screen__feedback">
        {tracksLoading ? <p>Loading secondary tracks...</p> : null}
        {submitting ? <p>Simulating eligibility...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
      </div>

      {!submitting && !error && incompleteData === true ? (
        <div className="eligibility-simulation-screen__incomplete" role="alert">
          <p>{message}</p>
        </div>
      ) : null}

      {!submitting && !error && incompleteData === false ? (
        <div className="eligibility-simulation-screen__results">
          <ul>
            {eligibleCourses.map((course) => (
              <li key={course.id}>{course.name}</li>
            ))}
          </ul>
          <button type="button" onClick={onContinue}>
            Continue
          </button>
        </div>
      ) : null}
    </section>
  );
}

export default EligibilitySimulationScreen;
