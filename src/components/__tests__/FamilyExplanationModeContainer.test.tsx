import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { FamilyExplanationModeContainer } from "../FamilyExplanationModeContainer";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

function mockRouter(responses: Record<string, unknown>) {
  fetchMock.mockImplementation(async (url: string) => {
    const matchedKey = Object.keys(responses).find((key) => url.includes(key));
    const body = matchedKey ? responses[matchedKey] : {};
    return {
      ok: true,
      json: async () => body,
    };
  });
}

test("displays the institutional confirmation alert when present", async () => {
  mockRouter({
    "institutional-confirmation-notification": {
      alert_present: true,
      alert_message: "Certain academic choices require confirmation from official institutions.",
    },
    "exploration-path": {
      interests_explanation: "The student is interested in: Robotics.",
      motivations_explanation: "The student is motivated by: Wants to help people.",
      academic_areas_explanation: "The student is strong in Math.",
      no_data: false,
    },
    "guidance-outcomes": { recommendations: [], pending: true },
  });

  render(
    <FamilyExplanationModeContainer bearerToken="token" studentSessionId="session-1" />,
  );

  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Certain academic choices require confirmation from official institutions.",
  );
});

test("shows no alert when no institutional confirmation alert is present", async () => {
  mockRouter({
    "institutional-confirmation-notification": { alert_present: false, alert_message: "" },
    "exploration-path": {
      interests_explanation: "This student has not started exploring yet.",
      motivations_explanation: "This student has not started exploring yet.",
      academic_areas_explanation: "This student has not started exploring yet.",
      no_data: true,
    },
    "guidance-outcomes": { recommendations: [], pending: true },
  });

  render(
    <FamilyExplanationModeContainer bearerToken="token" studentSessionId="session-2" />,
  );

  await screen.findByText("Family explanation mode");
  await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
});

test("allows closing the confirmation alert while the rest of the explanation screens remain", async () => {
  mockRouter({
    "institutional-confirmation-notification": {
      alert_present: true,
      alert_message: "Certain academic choices require confirmation from official institutions.",
    },
    "exploration-path": {
      interests_explanation: "The student is interested in: Robotics.",
      motivations_explanation: "The student is motivated by: Wants to help people.",
      academic_areas_explanation: "The student is strong in Math.",
      no_data: false,
    },
    "guidance-outcomes": { recommendations: [], pending: true },
  });

  render(
    <FamilyExplanationModeContainer bearerToken="token" studentSessionId="session-3" />,
  );

  await screen.findByRole("alert");
  const exploration = await screen.findByText("The student is interested in: Robotics.");

  fireEvent.click(screen.getByRole("button", { name: "Close" }));

  await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
  expect(exploration).toBeInTheDocument();
});

test("does not block the rest of the explanation screens when the confirmation notification request fails", async () => {
  fetchMock.mockImplementation(async (url: string) => {
    if (url.includes("institutional-confirmation-notification")) {
      return { ok: false, json: async () => ({ message: "Unable to load." }) };
    }
    if (url.includes("exploration-path")) {
      return {
        ok: true,
        json: async () => ({
          interests_explanation: "The student is interested in: Robotics.",
          motivations_explanation: "The student is motivated by: Wants to help people.",
          academic_areas_explanation: "The student is strong in Math.",
          no_data: false,
        }),
      };
    }
    return { ok: true, json: async () => ({ recommendations: [], pending: true }) };
  });

  render(
    <FamilyExplanationModeContainer bearerToken="token" studentSessionId="session-4" />,
  );

  expect(
    await screen.findByText("The student is interested in: Robotics."),
  ).toBeInTheDocument();
});
