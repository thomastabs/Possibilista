import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { ExplorationPathExplanationScreen } from "../ExplorationPathExplanationScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("displays the student's interests, motivations, and academic areas in accessible language", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      interests_explanation: "The student is interested in: Robotics.",
      motivations_explanation: "The student is motivated by: Wants to help people.",
      academic_areas_explanation: "The student is strong in Math; and working to improve History.",
      no_data: false,
    }),
  });

  render(
    <ExplorationPathExplanationScreen bearerToken="token" studentSessionId="session-1" />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

  expect(await screen.findByText("The student is interested in: Robotics.")).toBeInTheDocument();
  expect(
    screen.getByText("The student is motivated by: Wants to help people."),
  ).toBeInTheDocument();
  expect(
    screen.getByText("The student is strong in Math; and working to improve History."),
  ).toBeInTheDocument();
  expect(screen.getByText("Interests")).toBeInTheDocument();
  expect(screen.getByText("Motivations")).toBeInTheDocument();
  expect(screen.getByText("Academic areas")).toBeInTheDocument();
});

test("shows a no-data message when the student has not started exploring", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      interests_explanation: "This student has not started exploring yet.",
      motivations_explanation: "This student has not started exploring yet.",
      academic_areas_explanation: "This student has not started exploring yet.",
      no_data: true,
    }),
  });

  render(
    <ExplorationPathExplanationScreen bearerToken="token" studentSessionId="session-2" />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

  expect(await screen.findByRole("status")).toHaveTextContent(
    "This student has not started exploring yet.",
  );
  expect(screen.queryByText("Interests")).not.toBeInTheDocument();
});
