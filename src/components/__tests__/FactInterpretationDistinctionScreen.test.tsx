import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { FactInterpretationDistinctionScreen } from "../FactInterpretationDistinctionScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("renders factual information distinctly from interpretations", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      facts: ["The professional track leads to a secondary qualification."],
      interpretations: ["This may suit a student who prefers hands-on learning."],
      unavailable_info: false,
    }),
  });

  render(
    <FactInterpretationDistinctionScreen bearerToken="token" explanationId="explanation-1" />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

  expect(screen.getByText("Factual Information")).toBeInTheDocument();
  expect(
    screen.getByText("The professional track leads to a secondary qualification."),
  ).toBeInTheDocument();
  expect(screen.getByText("Interpretations and Suggestions")).toBeInTheDocument();
  expect(
    screen.getByText("This may suit a student who prefers hands-on learning."),
  ).toBeInTheDocument();
});

test("handles API errors gracefully by showing an error message", async () => {
  fetchMock.mockResolvedValue({
    ok: false,
    json: async () => ({ message: "Explanation not found." }),
  });

  render(
    <FactInterpretationDistinctionScreen bearerToken="token" explanationId="explanation-2" />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(await screen.findByRole("alert")).toHaveTextContent("Explanation not found.");
});
