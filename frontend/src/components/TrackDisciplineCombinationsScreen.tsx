import React, { useEffect, useState } from "react";

type SecondaryTrackDisciplineCombinationsResponse = {
  valid: boolean;
  trienais: string[];
  bienais: string[];
  anuais: string[];
  combinations: string[];
  message: string;
};

type TrackDisciplineCombinationsScreenProps = {
  bearerToken?: string | null;
  trackId: string;
  onBack?: () => void;
};

export function TrackDisciplineCombinationsScreen({
  bearerToken,
  trackId,
  onBack,
}: TrackDisciplineCombinationsScreenProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [valid, setValid] = useState<boolean | null>(null);
  const [trienais, setTrienais] = useState<string[]>([]);
  const [bienais, setBienais] = useState<string[]>([]);
  const [anuais, setAnuais] = useState<string[]>([]);
  const [combinations, setCombinations] = useState<string[]>([]);
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    const fetchDisciplineCombinations = async () => {
      setLoading(true);
      setError(null);

      try {
        const headers: Record<string, string> = {};
        if (bearerToken) {
          headers.Authorization = `Bearer ${bearerToken}`;
        }

        const apiResponse = await fetch(
          `/api/v1/secondary-tracks/${trackId}/discipline-combinations`,
          { headers },
        );

        const data: SecondaryTrackDisciplineCombinationsResponse = await apiResponse
          .json()
          .catch(() => ({
            valid: false,
            trienais: [],
            bienais: [],
            anuais: [],
            combinations: [],
            message: "",
          }));

        if (!apiResponse.ok) {
          throw new Error(data.message || "Unable to load discipline combinations for this track.");
        }

        if (cancelled) {
          return;
        }

        setValid(data.valid);
        setTrienais(data.trienais || []);
        setBienais(data.bienais || []);
        setAnuais(data.anuais || []);
        setCombinations(data.combinations || []);
        setMessage(data.message || "");
      } catch (fetchError) {
        if (cancelled) {
          return;
        }
        const errorMessage =
          fetchError instanceof Error
            ? fetchError.message
            : "Unable to load discipline combinations for this track.";
        setError(errorMessage);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchDisciplineCombinations();

    return () => {
      cancelled = true;
    };
  }, [bearerToken, trackId]);

  return (
    <section
      aria-labelledby="track-discipline-combinations-title"
      className="track-discipline-combinations-screen"
    >
      <header className="track-discipline-combinations-screen__header">
        <h1 id="track-discipline-combinations-title">Track discipline combinations</h1>
        <button type="button" onClick={onBack}>
          Back to secondary tracks
        </button>
      </header>

      <div aria-live="polite" className="track-discipline-combinations-screen__feedback">
        {loading ? <p>Loading discipline combinations...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
      </div>

      {!loading && !error && valid === true ? (
        <div className="track-discipline-combinations-screen__content">
          <section aria-labelledby="trienais-heading">
            <h2 id="trienais-heading">Trienais disciplines</h2>
            <ul>
              {trienais.map((discipline) => (
                <li key={discipline}>{discipline}</li>
              ))}
            </ul>
          </section>

          <section aria-labelledby="bienais-heading">
            <h2 id="bienais-heading">Bienais disciplines</h2>
            <ul>
              {bienais.map((discipline) => (
                <li key={discipline}>{discipline}</li>
              ))}
            </ul>
          </section>

          <section aria-labelledby="anuais-heading">
            <h2 id="anuais-heading">Anuais disciplines</h2>
            <ul>
              {anuais.map((discipline) => (
                <li key={discipline}>{discipline}</li>
              ))}
            </ul>
          </section>

          <section aria-labelledby="combinations-heading">
            <h2 id="combinations-heading">Valid combinations</h2>
            <ul>
              {combinations.map((combination) => (
                <li key={combination}>{combination}</li>
              ))}
            </ul>
          </section>
        </div>
      ) : null}

      {!loading && !error && valid === false ? (
        <div className="track-discipline-combinations-screen__invalid" role="alert">
          <p>{message}</p>
        </div>
      ) : null}
    </section>
  );
}

export default TrackDisciplineCombinationsScreen;
