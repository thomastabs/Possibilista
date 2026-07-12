import React from "react";
import { ExplorationPathExplanationScreen } from "./ExplorationPathExplanationScreen";
import { FactInterpretationDistinctionScreen } from "./FactInterpretationDistinctionScreen";
import { GuidanceOutcomesExplanationScreen } from "./GuidanceOutcomesExplanationScreen";
import { InstitutionalConfirmationNotificationScreen } from "./InstitutionalConfirmationNotificationScreen";

type FamilyExplanationModeContainerProps = {
  bearerToken?: string | null;
  studentSessionId?: string | null;
  explanationId?: string | null;
};

export function FamilyExplanationModeContainer({
  bearerToken,
  studentSessionId,
  explanationId,
}: FamilyExplanationModeContainerProps) {
  return (
    <section
      aria-labelledby="family-explanation-mode-title"
      className="family-explanation-mode"
    >
      <header>
        <h1 id="family-explanation-mode-title">Family explanation mode</h1>
        <p>A plain-language look at the student's academic planning, grounded in official sources.</p>
      </header>

      <InstitutionalConfirmationNotificationScreen
        bearerToken={bearerToken}
        studentSessionId={studentSessionId}
      />

      <ExplorationPathExplanationScreen
        bearerToken={bearerToken}
        studentSessionId={studentSessionId}
      />

      <GuidanceOutcomesExplanationScreen
        bearerToken={bearerToken}
        studentSessionId={studentSessionId}
      />

      {explanationId ? (
        <FactInterpretationDistinctionScreen
          bearerToken={bearerToken}
          explanationId={explanationId}
        />
      ) : null}
    </section>
  );
}

export default FamilyExplanationModeContainer;
