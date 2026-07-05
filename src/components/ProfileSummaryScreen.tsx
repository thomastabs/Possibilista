import React, { useEffect, useState } from "react";

type ProfileSummaryScreenProps = {
  bearerToken?: string | null;
  onNavigate?: (path: string) => void;
  nextPath?: string;
};

type ProfileSummaryResponse = {
  status?: string;
  profile_summary?: string;
  missing_fields?: string[];
  recommendations?: string[];
  message?: string;
};

const DEFAULT_NEXT_PATH = "/next-step";

export function ProfileSummaryScreen({
  bearerToken,
  onNavigate,
  nextPath = DEFAULT_NEXT_PATH,
}: ProfileSummaryScreenProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<string>("");
  const [missingFields, setMissingFields] = useState<string[]>([]);
  const [recommendations, setRecommendations] = useState<string[]>([]);

  useEffect(() => {
    let active = true;

    const loadSummary = async () => {
      if (!bearerToken) {
        setError("You must be signed in to view the profile summary.");
        setLoading(false);
        return;
      }

      try {
        const response = await fetch("/api/v1/profiling/summary", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${bearerToken}`,
          },
        });

        const data: ProfileSummaryResponse = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(data.message || "Unable to load profile summary.");
        }

        if (!active) {
          return;
        }

        setSummary(data.profile_summary || "");
        setMissingFields(data.missing_fields || []);
        setRecommendations(data.recommendations || []);
      } catch (loadError) {
        if (!active) {
          return;
        }

        const message =
          loadError instanceof Error ? loadError.message : "Unable to load profile summary.";
        setError(message);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadSummary();

    return () => {
      active = false;
    };
  }, [bearerToken]);

  const handleContinue = () => {
    if (onNavigate) {
      onNavigate(nextPath);
      return;
    }

    if (typeof window !== "undefined") {
      window.location.assign(nextPath);
    }
  };

  return (
    <section aria-labelledby="profile-summary-title" className="profile-summary-screen">
      <header>
        <h1 id="profile-summary-title">Profile summary</h1>
        <p>Review the collected profile and the current guidance notes.</p>
      </header>

      {loading ? <p>Loading profile summary...</p> : null}
      {error ? <p role="alert">{error}</p> : null}

      {!loading && !error ? (
        <>
          <article className="profile-summary-screen__summary">
            <h2>Summary</h2>
            <p>{summary || "No summary available yet."}</p>
          </article>

          <article className="profile-summary-screen__missing">
            <h2>Missing information</h2>
            {missingFields.length > 0 ? (
              <ul>
                {missingFields.map((field) => (
                  <li key={field}>{field}</li>
                ))}
              </ul>
            ) : (
              <p>No missing fields.</p>
            )}
          </article>

          <article className="profile-summary-screen__recommendations">
            <h2>Recommendations</h2>
            {recommendations.length > 0 ? (
              <ul>
                {recommendations.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p>No recommendations available yet.</p>
            )}
          </article>

          <div className="profile-summary-screen__actions">
            <button type="button" onClick={handleContinue}>
              Continue
            </button>
          </div>
        </>
      ) : null}
    </section>
  );
}

export default ProfileSummaryScreen;
