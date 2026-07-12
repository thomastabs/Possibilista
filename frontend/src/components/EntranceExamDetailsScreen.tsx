import React, { useEffect, useState } from "react";

type EntranceExam = {
  name: string;
  weight: number;
};

type HigherEdCourseEntranceExamsResponse = {
  available: boolean;
  exams: EntranceExam[];
  message: string;
};

type EntranceExamDetailsScreenProps = {
  bearerToken?: string | null;
  courseId: string;
  onBack?: () => void;
};

const formatWeight = (weight: number) => `${Math.round(weight * 100)}%`;

export function EntranceExamDetailsScreen({
  bearerToken,
  courseId,
  onBack,
}: EntranceExamDetailsScreenProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [available, setAvailable] = useState<boolean | null>(null);
  const [exams, setExams] = useState<EntranceExam[]>([]);
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    const fetchEntranceExams = async () => {
      setLoading(true);
      setError(null);

      try {
        const headers: Record<string, string> = {};
        if (bearerToken) {
          headers.Authorization = `Bearer ${bearerToken}`;
        }

        const apiResponse = await fetch(
          `/api/v1/higher-ed/courses/${courseId}/entrance-exams`,
          { headers },
        );

        const data: HigherEdCourseEntranceExamsResponse = await apiResponse
          .json()
          .catch(() => ({ available: false, exams: [], message: "" }));

        if (!apiResponse.ok) {
          throw new Error(
            data.message || "Unable to load entrance exam requirements for this course.",
          );
        }

        if (cancelled) {
          return;
        }

        setAvailable(data.available);
        setExams(data.exams || []);
        setMessage(data.message || "");
      } catch (fetchError) {
        if (cancelled) {
          return;
        }
        const errorMessage =
          fetchError instanceof Error
            ? fetchError.message
            : "Unable to load entrance exam requirements for this course.";
        setError(errorMessage);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchEntranceExams();

    return () => {
      cancelled = true;
    };
  }, [bearerToken, courseId]);

  return (
    <section
      aria-labelledby="entrance-exam-details-title"
      className="entrance-exam-details-screen"
    >
      <header className="entrance-exam-details-screen__header">
        <h1 id="entrance-exam-details-title">Entrance exam requirements</h1>
        <button type="button" onClick={onBack}>
          Back
        </button>
      </header>

      <div aria-live="polite" className="entrance-exam-details-screen__feedback">
        {loading ? <p>Loading entrance exam requirements...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
      </div>

      {!loading && !error && available === true ? (
        <table className="entrance-exam-details-screen__table">
          <thead>
            <tr>
              <th scope="col">Exam</th>
              <th scope="col">Weight</th>
            </tr>
          </thead>
          <tbody>
            {exams.map((exam) => (
              <tr key={exam.name}>
                <td>{exam.name}</td>
                <td>{formatWeight(exam.weight)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}

      {!loading && !error && available === false ? (
        <div className="entrance-exam-details-screen__unavailable" role="status">
          <p>{message}</p>
        </div>
      ) : null}
    </section>
  );
}

export default EntranceExamDetailsScreen;
