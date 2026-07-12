import React, { useEffect, useState } from "react";

type ExamRequirement = {
  name: string;
  timing: string;
};

type SecondaryTrackExamRequirementsResponse = {
  valid: boolean;
  exams: ExamRequirement[];
  message: string;
};

type TrackExamRequirementsScreenProps = {
  bearerToken?: string | null;
  trackId: string;
  onBack?: () => void;
};

export function TrackExamRequirementsScreen({
  bearerToken,
  trackId,
  onBack,
}: TrackExamRequirementsScreenProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [valid, setValid] = useState<boolean | null>(null);
  const [exams, setExams] = useState<ExamRequirement[]>([]);
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    const fetchExamRequirements = async () => {
      setLoading(true);
      setError(null);

      try {
        const headers: Record<string, string> = {};
        if (bearerToken) {
          headers.Authorization = `Bearer ${bearerToken}`;
        }

        const apiResponse = await fetch(
          `/api/v1/secondary-tracks/${trackId}/exam-requirements`,
          { headers },
        );

        const data: SecondaryTrackExamRequirementsResponse = await apiResponse
          .json()
          .catch(() => ({ valid: false, exams: [], message: "" }));

        if (!apiResponse.ok) {
          throw new Error(data.message || "Unable to load exam requirements for this track.");
        }

        if (cancelled) {
          return;
        }

        setValid(data.valid);
        setExams(data.exams || []);
        setMessage(data.message || "");
      } catch (fetchError) {
        if (cancelled) {
          return;
        }
        const errorMessage =
          fetchError instanceof Error
            ? fetchError.message
            : "Unable to load exam requirements for this track.";
        setError(errorMessage);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchExamRequirements();

    return () => {
      cancelled = true;
    };
  }, [bearerToken, trackId]);

  return (
    <section aria-labelledby="track-exam-requirements-title" className="track-exam-requirements-screen">
      <header className="track-exam-requirements-screen__header">
        <h1 id="track-exam-requirements-title">Track exam requirements</h1>
        <button type="button" onClick={onBack}>
          Back to secondary tracks
        </button>
      </header>

      <div aria-live="polite" className="track-exam-requirements-screen__feedback">
        {loading ? <p>Loading exam requirements...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
      </div>

      {!loading && !error && valid === true ? (
        <table className="track-exam-requirements-screen__table">
          <thead>
            <tr>
              <th scope="col">Exam</th>
              <th scope="col">Timing</th>
            </tr>
          </thead>
          <tbody>
            {exams.map((exam) => (
              <tr key={exam.name}>
                <td>{exam.name}</td>
                <td>{exam.timing}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}

      {!loading && !error && valid === false ? (
        <div className="track-exam-requirements-screen__invalid" role="alert">
          <p>{message}</p>
        </div>
      ) : null}
    </section>
  );
}

export default TrackExamRequirementsScreen;
