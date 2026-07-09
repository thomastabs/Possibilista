import React, { useEffect, useState } from "react";

type SecondaryTrackDisciplinesResponse = {
  valid: boolean;
  disciplines: string[];
  message: string;
};

type TrackDisciplinesScreenProps = {
  bearerToken?: string | null;
  trackId: string;
  onBack?: () => void;
};

export function TrackDisciplinesScreen({
  bearerToken,
  trackId,
  onBack,
}: TrackDisciplinesScreenProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [valid, setValid] = useState<boolean | null>(null);
  const [disciplines, setDisciplines] = useState<string[]>([]);
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    const fetchDisciplines = async () => {
      setLoading(true);
      setError(null);

      try {
        const headers: Record<string, string> = {};
        if (bearerToken) {
          headers.Authorization = `Bearer ${bearerToken}`;
        }

        const apiResponse = await fetch(
          `/api/v1/secondary-tracks/${trackId}/disciplines`,
          { headers },
        );

        const data: SecondaryTrackDisciplinesResponse = await apiResponse
          .json()
          .catch(() => ({ valid: false, disciplines: [], message: "" }));

        if (!apiResponse.ok) {
          throw new Error(data.message || "Unable to load disciplines for this track.");
        }

        if (cancelled) {
          return;
        }

        setValid(data.valid);
        setDisciplines(data.disciplines || []);
        setMessage(data.message || "");
      } catch (fetchError) {
        if (cancelled) {
          return;
        }
        const errorMessage =
          fetchError instanceof Error
            ? fetchError.message
            : "Unable to load disciplines for this track.";
        setError(errorMessage);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchDisciplines();

    return () => {
      cancelled = true;
    };
  }, [bearerToken, trackId]);

  return (
    <section aria-labelledby="track-disciplines-title" className="track-disciplines-screen">
      <header className="track-disciplines-screen__header">
        <h1 id="track-disciplines-title">Track disciplines</h1>
        <button type="button" onClick={onBack}>
          Back to secondary tracks
        </button>
      </header>

      <div aria-live="polite" className="track-disciplines-screen__feedback">
        {loading ? <p>Loading disciplines...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
      </div>

      {!loading && !error && valid === true ? (
        <ul className="track-disciplines-screen__list">
          {disciplines.map((discipline) => (
            <li key={discipline}>{discipline}</li>
          ))}
        </ul>
      ) : null}

      {!loading && !error && valid === false ? (
        <div className="track-disciplines-screen__invalid" role="alert">
          <p>{message}</p>
          <p>Please ask about one of the valid secondary tracks.</p>
        </div>
      ) : null}
    </section>
  );
}

export default TrackDisciplinesScreen;
