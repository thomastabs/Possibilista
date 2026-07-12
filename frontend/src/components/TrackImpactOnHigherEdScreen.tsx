import React, { useEffect, useState } from "react";

type SecondaryTrackHigherEdImpactResponse = {
  valid: boolean;
  impact_description: string;
  message: string;
};

type TrackImpactOnHigherEdScreenProps = {
  bearerToken?: string | null;
  trackId: string;
  onBack?: () => void;
};

export function TrackImpactOnHigherEdScreen({
  bearerToken,
  trackId,
  onBack,
}: TrackImpactOnHigherEdScreenProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [valid, setValid] = useState<boolean | null>(null);
  const [impactDescription, setImpactDescription] = useState<string>("");
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    const fetchHigherEdImpact = async () => {
      setLoading(true);
      setError(null);

      try {
        const headers: Record<string, string> = {};
        if (bearerToken) {
          headers.Authorization = `Bearer ${bearerToken}`;
        }

        const apiResponse = await fetch(
          `/api/v1/secondary-tracks/${trackId}/higher-ed-impact`,
          { headers },
        );

        const data: SecondaryTrackHigherEdImpactResponse = await apiResponse
          .json()
          .catch(() => ({ valid: false, impact_description: "", message: "" }));

        if (!apiResponse.ok) {
          throw new Error(
            data.message || "Unable to load higher education impact information for this track.",
          );
        }

        if (cancelled) {
          return;
        }

        setValid(data.valid);
        setImpactDescription(data.impact_description || "");
        setMessage(data.message || "");
      } catch (fetchError) {
        if (cancelled) {
          return;
        }
        const errorMessage =
          fetchError instanceof Error
            ? fetchError.message
            : "Unable to load higher education impact information for this track.";
        setError(errorMessage);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchHigherEdImpact();

    return () => {
      cancelled = true;
    };
  }, [bearerToken, trackId]);

  return (
    <section
      aria-labelledby="track-impact-on-higher-ed-title"
      className="track-impact-on-higher-ed-screen"
    >
      <header className="track-impact-on-higher-ed-screen__header">
        <h1 id="track-impact-on-higher-ed-title">Impact on higher education</h1>
        <button type="button" onClick={onBack}>
          Back to secondary tracks
        </button>
      </header>

      <div aria-live="polite" className="track-impact-on-higher-ed-screen__feedback">
        {loading ? <p>Loading higher education impact...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
      </div>

      {!loading && !error && valid === true ? (
        <div className="track-impact-on-higher-ed-screen__content">
          <p>{impactDescription}</p>
        </div>
      ) : null}

      {!loading && !error && valid === false ? (
        <div className="track-impact-on-higher-ed-screen__invalid" role="alert">
          <p>{message}</p>
        </div>
      ) : null}
    </section>
  );
}

export default TrackImpactOnHigherEdScreen;
