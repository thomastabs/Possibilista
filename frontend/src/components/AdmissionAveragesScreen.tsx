import React, { useEffect, useState } from "react";

type ExamWeight = {
  exam_name: string;
  weight: number;
};

type HigherEdCourseAdmissionAveragesResponse = {
  available: boolean;
  admission_average: number | null;
  exam_weights: ExamWeight[];
  message: string;
};

type AdmissionAveragesScreenProps = {
  bearerToken?: string | null;
  courseId: string;
  onBack?: () => void;
};

const formatWeight = (weight: number) => `${Math.round(weight * 100)}%`;

export function AdmissionAveragesScreen({
  bearerToken,
  courseId,
  onBack,
}: AdmissionAveragesScreenProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [available, setAvailable] = useState<boolean | null>(null);
  const [admissionAverage, setAdmissionAverage] = useState<number | null>(null);
  const [examWeights, setExamWeights] = useState<ExamWeight[]>([]);
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    const fetchAdmissionAverages = async () => {
      setLoading(true);
      setError(null);

      try {
        const headers: Record<string, string> = {};
        if (bearerToken) {
          headers.Authorization = `Bearer ${bearerToken}`;
        }

        const apiResponse = await fetch(
          `/api/v1/higher-ed/courses/${courseId}/admission-averages`,
          { headers },
        );

        const data: HigherEdCourseAdmissionAveragesResponse = await apiResponse
          .json()
          .catch(() => ({ available: false, admission_average: null, exam_weights: [], message: "" }));

        if (!apiResponse.ok) {
          throw new Error(
            data.message || "Unable to load admission averages for this course.",
          );
        }

        if (cancelled) {
          return;
        }

        setAvailable(data.available);
        setAdmissionAverage(data.admission_average ?? null);
        setExamWeights(data.exam_weights || []);
        setMessage(data.message || "");
      } catch (fetchError) {
        if (cancelled) {
          return;
        }
        const errorMessage =
          fetchError instanceof Error
            ? fetchError.message
            : "Unable to load admission averages for this course.";
        setError(errorMessage);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchAdmissionAverages();

    return () => {
      cancelled = true;
    };
  }, [bearerToken, courseId]);

  return (
    <section aria-labelledby="admission-averages-title" className="admission-averages-screen">
      <header className="admission-averages-screen__header">
        <h1 id="admission-averages-title">Admission averages</h1>
        <button type="button" onClick={onBack}>
          Back
        </button>
      </header>

      <div aria-live="polite" className="admission-averages-screen__feedback">
        {loading ? <p>Loading admission averages...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
      </div>

      {!loading && !error && available === true ? (
        <div className="admission-averages-screen__content">
          <p className="admission-averages-screen__average">
            Admission average: {admissionAverage !== null ? admissionAverage.toFixed(2) : ""}
          </p>
          <table className="admission-averages-screen__table">
            <thead>
              <tr>
                <th scope="col">Exam</th>
                <th scope="col">Weight</th>
              </tr>
            </thead>
            <tbody>
              {examWeights.map((exam) => (
                <tr key={exam.exam_name}>
                  <td>{exam.exam_name}</td>
                  <td>{formatWeight(exam.weight)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {!loading && !error && available === false ? (
        <div className="admission-averages-screen__unavailable" role="status">
          <p>{message}</p>
        </div>
      ) : null}
    </section>
  );
}

export default AdmissionAveragesScreen;
