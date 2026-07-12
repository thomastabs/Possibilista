import React, { useEffect, useState } from "react";

type ExplorationPathResponse = {
  interests_explanation?: string;
  motivations_explanation?: string;
  academic_areas_explanation?: string;
  no_data?: boolean;
  message?: string;
};

type ExplorationPathExplanationScreenProps = {
  bearerToken?: string | null;
  studentSessionId?: string | null;
};

export function ExplorationPathExplanationScreen({
  bearerToken,
  studentSessionId,
}: ExplorationPathExplanationScreenProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [interestsExplanation, setInterestsExplanation] = useState("");
  const [motivationsExplanation, setMotivationsExplanation] = useState("");
  const [academicAreasExplanation, setAcademicAreasExplanation] = useState("");
  const [noData, setNoData] = useState(false);

  useEffect(() => {
    let active = true;

    const loadExplorationPath = async () => {
      if (!bearerToken) {
        setError("You must be signed in to view the exploration path.");
        setLoading(false);
        return;
      }

      if (!studentSessionId) {
        setError("A student session id is required to view the exploration path.");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `/api/v1/family/exploration-path?student_session_id=${encodeURIComponent(
            studentSessionId,
          )}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${bearerToken}`,
            },
          },
        );

        const data: ExplorationPathResponse = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(data.message || "Unable to load the exploration path.");
        }

        if (!active) {
          return;
        }

        setInterestsExplanation(data.interests_explanation || "");
        setMotivationsExplanation(data.motivations_explanation || "");
        setAcademicAreasExplanation(data.academic_areas_explanation || "");
        setNoData(Boolean(data.no_data));
      } catch (loadError) {
        if (!active) {
          return;
        }

        const message =
          loadError instanceof Error ? loadError.message : "Unable to load the exploration path.";
        setError(message);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadExplorationPath();

    return () => {
      active = false;
    };
  }, [bearerToken, studentSessionId]);

  return (
    <section aria-labelledby="exploration-path-title" className="exploration-path-screen">
      <header>
        <h1 id="exploration-path-title">Student exploration path</h1>
        <p>A plain-language look at what the student has explored so far.</p>
      </header>

      {loading ? <p>Loading exploration path...</p> : null}
      {error ? <p role="alert">{error}</p> : null}

      {!loading && !error && noData ? (
        <p role="status">
          {interestsExplanation || "This student has not started exploring yet."}
        </p>
      ) : null}

      {!loading && !error && !noData ? (
        <>
          <article className="exploration-path-screen__interests">
            <h2>Interests</h2>
            <p>{interestsExplanation}</p>
          </article>

          <article className="exploration-path-screen__motivations">
            <h2>Motivations</h2>
            <p>{motivationsExplanation}</p>
          </article>

          <article className="exploration-path-screen__academic-areas">
            <h2>Academic areas</h2>
            <p>{academicAreasExplanation}</p>
          </article>
        </>
      ) : null}
    </section>
  );
}

export default ExplorationPathExplanationScreen;
