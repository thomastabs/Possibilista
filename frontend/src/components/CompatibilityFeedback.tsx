import React from "react";

type CompatibilityFeedbackProps = {
  compatible: boolean;
  message: string;
};

const looksLikeInputPrompt = (message: string) => {
  const normalized = message.toLowerCase();
  return normalized.includes("correct") || normalized.includes("complete");
};

export function CompatibilityFeedback({ compatible, message }: CompatibilityFeedbackProps) {
  if (compatible) {
    return (
      <div className="compatibility-feedback compatibility-feedback--compatible" role="status">
        <p>{message}</p>
      </div>
    );
  }

  if (looksLikeInputPrompt(message)) {
    return (
      <div className="compatibility-feedback compatibility-feedback--input-prompt" role="alert">
        <p>{message}</p>
      </div>
    );
  }

  return (
    <div className="compatibility-feedback compatibility-feedback--no-matches" role="status">
      <p>{message}</p>
    </div>
  );
}

export default CompatibilityFeedback;
