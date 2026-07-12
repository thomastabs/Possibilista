import React, { useEffect, useState } from "react";

type FactInterpretationResponse = {
  facts?: string[];
  interpretations?: string[];
  no_basis?: boolean;
  message?: string;
};

type AnswerFactInterpretationScreenProps = {
  bearerToken?: string | null;
  answerId?: string | null;
  onClose?: () => void;
};

const NO_BASIS_MESSAGE =
  "The system cannot provide an interpretation for this because no source information is available.";

export function AnswerFactInterpretationScreen({
  bearerToken,
  answerId,
  onClose,
}: AnswerFactInterpretationScreenProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [facts, setFacts] = useState<string[]>([]);
  const [interpretations, setInterpretations] = useState<string[]>([]);
  const [noBasis, setNoBasis] = useState(false);

  useEffect(() => {
    let active = true;

    const loadFactInterpretation = async () => {
      if (!bearerToken) {
        setError("You must be signed in to view this answer.");
        setLoading(false);
        return;
      }

      if (!answerId) {
        setError("An answer id is required to view this answer.");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `/api/v1/answers/fact-interpretation?answer_id=${encodeURIComponent(answerId)}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${bearerToken}`,
            },
          },
        );

        const data: FactInterpretationResponse = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(data.message || "Unable to load this answer.");
        }

        if (!active) {
          return;
        }

        setFacts(data.facts || []);
        setInterpretations(data.interpretations || []);
        setNoBasis(Boolean(data.no_basis));
      } catch (loadError) {
        if (!active) {
          return;
        }

        const message =
          loadError instanceof Error ? loadError.message : "Unable to load this answer.";
        setError(message);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadFactInterpretation();

    return () => {
      active = false;
    };
  }, [bearerToken, answerId]);

  return (
    <section
      aria-labelledby="answer-fact-interpretation-title"
      className="answer-fact-interpretation-screen"
    >
      <header className="answer-fact-interpretation-screen__header">
        <h1 id="answer-fact-interpretation-title">Answer breakdown</h1>
        {onClose ? (
          <button type="button" onClick={onClose}>
            Close
          </button>
        ) : null}
      </header>

      {loading ? <p>Loading answer...</p> : null}
      {error ? <p role="alert">{error}</p> : null}

      {!loading && !error && noBasis ? <p role="status">{NO_BASIS_MESSAGE}</p> : null}

      {!loading && !error && !noBasis ? (
        <>
          <article className="answer-fact-interpretation-screen__facts">
            <h2>Facts</h2>
            {facts.length > 0 ? (
              <ul>
                {facts.map((fact) => (
                  <li key={fact}>{fact}</li>
                ))}
              </ul>
            ) : (
              <p>No facts available.</p>
            )}
          </article>

          <article className="answer-fact-interpretation-screen__interpretations">
            <h2>Interpretations</h2>
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

export default AnswerFactInterpretationScreen;
