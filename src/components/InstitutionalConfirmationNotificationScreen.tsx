import React, { useEffect, useState } from "react";

type InstitutionalConfirmationNotificationResponse = {
  alert_present?: boolean;
  alert_message?: string;
  message?: string;
};

type InstitutionalConfirmationNotificationScreenProps = {
  bearerToken?: string | null;
  studentSessionId?: string | null;
};

export function InstitutionalConfirmationNotificationScreen({
  bearerToken,
  studentSessionId,
}: InstitutionalConfirmationNotificationScreenProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [alertPresent, setAlertPresent] = useState(false);
  const [alertMessage, setAlertMessage] = useState("");

  useEffect(() => {
    let active = true;

    const loadConfirmationNotification = async () => {
      if (!bearerToken) {
        setError("You must be signed in to view confirmation notifications.");
        setLoading(false);
        return;
      }

      if (!studentSessionId) {
        setError("A student session id is required to view confirmation notifications.");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `/api/v1/family/institutional-confirmation-notification?student_session_id=${encodeURIComponent(
            studentSessionId,
          )}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${bearerToken}`,
            },
          },
        );

        const data: InstitutionalConfirmationNotificationResponse = await response
          .json()
          .catch(() => ({}));

        if (!response.ok) {
          throw new Error(data.message || "Unable to load confirmation notifications.");
        }

        if (!active) {
          return;
        }

        setAlertPresent(Boolean(data.alert_present));
        setAlertMessage(data.alert_message || "");
      } catch (loadError) {
        if (!active) {
          return;
        }

        const message =
          loadError instanceof Error
            ? loadError.message
            : "Unable to load confirmation notifications.";
        setError(message);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadConfirmationNotification();

    return () => {
      active = false;
    };
  }, [bearerToken, studentSessionId]);

  if (loading) {
    return <p>Checking for confirmation notifications...</p>;
  }

  if (error) {
    return <p role="alert">{error}</p>;
  }

  if (!alertPresent) {
    return null;
  }

  return (
    <div
      role="alert"
      className="institutional-confirmation-notification"
      aria-label="Institutional confirmation notification"
    >
      <p>{alertMessage}</p>
    </div>
  );
}

export default InstitutionalConfirmationNotificationScreen;
