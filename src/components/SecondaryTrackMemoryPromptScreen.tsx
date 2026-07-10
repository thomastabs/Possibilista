import React, { useEffect, useState } from "react";

type SecondaryTrackMemoryResponse = {
  track_explored: boolean;
  stored_track_id: string | null;
  message: string;
};

type SecondaryTrackMemoryPromptScreenProps = {
  bearerToken?: string | null;
  sessionId?: string | null;
  onExploreTrack?: () => void;
  onAskQuestions?: (storedTrackId: string) => void;
};

export function SecondaryTrackMemoryPromptScreen({
  bearerToken,
  sessionId,
  onExploreTrack,
  onAskQuestions,
}: SecondaryTrackMemoryPromptScreenProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [trackExplored, setTrackExplored] = useState<boolean | null>(null);
  const [storedTrackId, setStoredTrackId] = useState<string | null>(null);
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    const fetchTrackMemory = async () => {
      if (!bearerToken || !sessionId) {
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const apiResponse = await fetch(
          `/api/v1/session/secondary-track-memory?session_id=${encodeURIComponent(sessionId)}`,
          { headers: { Authorization: `Bearer ${bearerToken}` } },
        );

        const data: SecondaryTrackMemoryResponse = await apiResponse
          .json()
          .catch(() => ({ track_explored: false, stored_track_id: null, message: "" }));

        if (!apiResponse.ok) {
          throw new Error(data.message || "Unable to load secondary track memory.");
        }

        if (cancelled) {
          return;
        }

        setTrackExplored(data.track_explored);
        setStoredTrackId(data.stored_track_id);
        setMessage(data.message || "");
      } catch (fetchError) {
        if (cancelled) {
          return;
        }
        const errorMessage =
          fetchError instanceof Error
            ? fetchError.message
            : "Unable to load secondary track memory.";
        setError(errorMessage);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchTrackMemory();

    return () => {
      cancelled = true;
    };
  }, [bearerToken, sessionId]);

  return (
    <section
      aria-labelledby="secondary-track-memory-prompt-title"
      className="secondary-track-memory-prompt-screen"
    >
      <h1 id="secondary-track-memory-prompt-title">Secondary track</h1>

      <div aria-live="polite" className="secondary-track-memory-prompt-screen__feedback">
        {loading ? <p>Loading secondary track memory...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
      </div>

      {!loading && !error && trackExplored === false ? (
        <div className="secondary-track-memory-prompt-screen__prompt" role="alert">
          <p>{message}</p>
          <button type="button" onClick={onExploreTrack}>
            Explore a secondary track
          </button>
        </div>
      ) : null}

      {!loading && !error && trackExplored === true && storedTrackId ? (
        <div className="secondary-track-memory-prompt-screen__confirmation" role="status">
          <p>{message}</p>
          <button type="button" onClick={() => onAskQuestions?.(storedTrackId)}>
            Ask follow-up questions
          </button>
          <button type="button" onClick={onExploreTrack}>
            Explore a different track
          </button>
        </div>
      ) : null}
    </section>
  );
}

export default SecondaryTrackMemoryPromptScreen;
