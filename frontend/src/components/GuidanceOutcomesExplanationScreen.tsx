import React, { useEffect, useState } from "react";

type GuidanceRecommendation = {
  text: string;
  source: string;
};

type GuidanceOutcomesResponse = {
  recommendations?: GuidanceRecommendation[];
  pending?: boolean;
  message?: string;
};

type GuidanceOutcomesExplanationScreenProps = {
  bearerToken?: string | null;
  studentSessionId?: string | null;
};

const PENDING_MESSAGE = "Guidance is still pending for this student.";

export function GuidanceOutcomesExplanationScreen({
  bearerToken,
  studentSessionId,
}: GuidanceOutcomesExplanationScreenProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<GuidanceRecommendation[]>([]);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    let active = true;

    const loadGuidanceOutcomes = async () => {
      if (!bearerToken) {
        setError("You must be signed in to view the guidance outcomes.");
        setLoading(false);
        return;
      }

      if (!studentSessionId) {
        setError("A student session id is required to view the guidance outcomes.");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `/api/v1/family/guidance-outcomes?student_session_id=${encodeURIComponent(
            studentSessionId,
          )}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${bearerToken}`,
            },
          },
        );

        const data: GuidanceOutcomesResponse = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(data.message || "Unable to load the guidance outcomes.");
        }

        if (!active) {
          return;
        }

        setRecommendations(data.recommendations || []);
        setPending(Boolean(data.pending));
      } catch (loadError) {
        if (!active) {
          return;
        }

        const message =
          loadError instanceof Error ? loadError.message : "Unable to load the guidance outcomes.";
        setError(message);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadGuidanceOutcomes();

    return () => {
      active = false;
    };
  }, [bearerToken, studentSessionId]);

  return (
    <section aria-labelledby="guidance-outcomes-title" className="guidance-outcomes-screen">
      <header>
        <h1 id="guidance-outcomes-title">Guidance outcomes</h1>
        <p>Recommendations for the student, each grounded in an official source.</p>
      </header>

      {loading ? <p>Loading guidance outcomes...</p> : null}
      {error ? <p role="alert">{error}</p> : null}

      {!loading && !error && pending ? <p role="status">{PENDING_MESSAGE}</p> : null}

      {!loading && !error && !pending ? (
        <ul className="guidance-outcomes-screen__recommendations">
          {recommendations.map((recommendation) => (
            <li key={recommendation.text}>
              <p>{recommendation.text}</p>
              <p className="guidance-outcomes-screen__source">Source: {recommendation.source}</p>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}

export default GuidanceOutcomesExplanationScreen;
