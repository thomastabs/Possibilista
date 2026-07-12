import React, { useEffect, useState } from "react";

type HigherEdCourse = {
  id: string;
  name: string;
};

type HigherEdCoursesResponse = {
  courses: HigherEdCourse[];
  message: string;
};

type CompatibleCoursesScreenProps = {
  bearerToken?: string | null;
  trackId: string;
  onBack?: () => void;
};

const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

const NO_DATA_MESSAGE = "No data is available for the entered secondary track.";

export function CompatibleCoursesScreen({
  bearerToken,
  trackId,
  onBack,
}: CompatibleCoursesScreenProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [courses, setCourses] = useState<HigherEdCourse[]>([]);
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    const fetchCompatibleCourses = async () => {
      setError(null);

      const trimmedTrackId = trackId.trim();
      if (!trimmedTrackId || !UUID_PATTERN.test(trimmedTrackId)) {
        setCourses([]);
        setMessage(NO_DATA_MESSAGE);
        return;
      }

      setLoading(true);

      try {
        const headers: Record<string, string> = {};
        if (bearerToken) {
          headers.Authorization = `Bearer ${bearerToken}`;
        }

        const apiResponse = await fetch(
          `/api/v1/higher-ed/courses?secondary_track_id=${encodeURIComponent(trimmedTrackId)}`,
          { headers },
        );

        const data: HigherEdCoursesResponse = await apiResponse
          .json()
          .catch(() => ({ courses: [], message: "" }));

        if (!apiResponse.ok) {
          throw new Error(data.message || "Unable to load compatible courses for this track.");
        }

        if (cancelled) {
          return;
        }

        setCourses(data.courses || []);
        setMessage(data.message || "");
      } catch (fetchError) {
        if (cancelled) {
          return;
        }
        const errorMessage =
          fetchError instanceof Error
            ? fetchError.message
            : "Unable to load compatible courses for this track.";
        setError(errorMessage);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchCompatibleCourses();

    return () => {
      cancelled = true;
    };
  }, [bearerToken, trackId]);

  return (
    <section
      aria-labelledby="compatible-courses-title"
      className="compatible-courses-screen"
    >
      <header className="compatible-courses-screen__header">
        <h1 id="compatible-courses-title">Compatible higher education courses</h1>
        <button type="button" onClick={onBack}>
          Back to secondary tracks
        </button>
      </header>

      <div aria-live="polite" className="compatible-courses-screen__feedback">
        {loading ? <p>Loading compatible courses...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
      </div>

      {!loading && !error && courses.length > 0 ? (
        <ul className="compatible-courses-screen__list">
          {courses.map((course) => (
            <li key={course.id}>{course.name}</li>
          ))}
        </ul>
      ) : null}

      {!loading && !error && courses.length === 0 && message ? (
        <div className="compatible-courses-screen__no-data" role="status">
          <p>{message}</p>
        </div>
      ) : null}
    </section>
  );
}

export default CompatibleCoursesScreen;
