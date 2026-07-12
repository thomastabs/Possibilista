import React, { useEffect, useState } from "react";

type FactInterpretationDistinctionResponse = {
  facts?: string[];
  interpretations?: string[];
  unavailable_info?: boolean;
  message?: string;
};

type FactInterpretationDistinctionScreenProps = {
  bearerToken?: string | null;
  explanationId?: string | null;
  onClose?: () => void;
};

const UNAVAILABLE_INFO_MESSAGE =
  "The system lacks a basis to answer this question or topic.";
const CONFIRMATION_SUGGESTION_MESSAGE =
  "Please seek human or institutional confirmation for this topic.";

export function FactInterpretationDistinctionScreen({
  bearerToken,
  explanationId,
  onClose,
}: FactInterpretationDistinctionScreenProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [facts, setFacts] = useState<string[]>([]);
  const [interpretations, setInterpretations] = useState<string[]>([]);
  const [unavailableInfo, setUnavailableInfo] = useState(false);

  useEffect(() => {
    let active = true;

    const loadFactInterpretationDistinction = async () => {
      if (!bearerToken) {
        setError("You must be signed in to view this explanation.");
        setLoading(false);
        return;
      }

      if (!explanationId) {
        setError("An explanation id is required to view this explanation.");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `/api/v1/family/fact-interpretation-distinction?explanation_id=${encodeURIComponent(
            explanationId,
          )}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${bearerToken}`,
            },
          },
        );

        const data: FactInterpretationDistinctionResponse = await response
          .json()
          .catch(() => ({}));

        if (!response.ok) {
          throw new Error(data.message || "Unable to load this explanation.");
        }

        if (!active) {
          return;
        }

        setFacts(data.facts || []);
        setInterpretations(data.interpretations || []);
        setUnavailableInfo(Boolean(data.unavailable_info));
      } catch (loadError) {
        if (!active) {
          return;
        }

        const message =
          loadError instanceof Error ? loadError.message : "Unable to load this explanation.";
        setError(message);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadFactInterpretationDistinction();

    return () => {
      active = false;
    };
  }, [bearerToken, explanationId]);

  return (
    <section
      aria-labelledby="fact-interpretation-distinction-title"
      className="fact-interpretation-screen"
    >
      <header className="fact-interpretation-screen__header">
        <h1 id="fact-interpretation-distinction-title">Explanation</h1>
        {onClose ? (
          <button type="button" onClick={onClose}>
            Close
          </button>
        ) : null}
      </header>

      {loading ? <p>Loading explanation...</p> : null}
      {error ? <p role="alert">{error}</p> : null}

      {!loading && !error && unavailableInfo ? (
        <div className="fact-interpretation-screen__unavailable">
          <p role="status">{UNAVAILABLE_INFO_MESSAGE}</p>
          <p role="alert">{CONFIRMATION_SUGGESTION_MESSAGE}</p>
        </div>
      ) : null}

      {!loading && !error && !unavailableInfo ? (
        <>
          <article className="fact-interpretation-screen__facts">
            <h2>Factual Information</h2>
            {facts.length > 0 ? (
              <ul>
                {facts.map((fact) => (
                  <li key={fact}>{fact}</li>
                ))}
              </ul>
            ) : (
              <p>No factual information available.</p>
            )}
          </article>

          <hr />

          <article className="fact-interpretation-screen__interpretations">
            <h2>Interpretations and Suggestions</h2>
            {interpretations.length > 0 ? (
              <ul>
                {interpretations.map((interpretation) => (
                  <li key={interpretation}>{interpretation}</li>
                ))}
              </ul>
            ) : (
              <p>No interpretations available.</p>
            )}
          </article>
        </>
      ) : null}
    </section>
  );
}

export default FactInterpretationDistinctionScreen;
