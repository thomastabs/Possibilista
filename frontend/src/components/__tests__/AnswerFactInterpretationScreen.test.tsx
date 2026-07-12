import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { AnswerFactInterpretationScreen } from "../AnswerFactInterpretationScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("renders facts and interpretations distinctly with the expected labels", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      facts: ["The professional track leads to a secondary qualification."],
      interpretations: ["This may suit a student who prefers hands-on learning."],
      no_basis: false,
    }),
  });

  render(<AnswerFactInterpretationScreen bearerToken="token" answerId="answer-1" />);

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

  expect(screen.getByText("Facts")).toBeInTheDocument();
  expect(
    screen.getByText("The professional track leads to a secondary qualification."),
  ).toBeInTheDocument();
  expect(screen.getByText("Interpretations")).toBeInTheDocument();
  expect(
    screen.getByText("This may suit a student who prefers hands-on learning."),
  ).toBeInTheDocument();
});

test("displays a clear message when no_basis is true", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      facts: [],
      interpretations: [],
      no_basis: true,
    }),
  });

  render(<AnswerFactInterpretationScreen bearerToken="token" answerId="answer-2" />);

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

  expect(await screen.findByRole("status")).toHaveTextContent(
    "The system cannot provide an interpretation for this because no source information is available.",
  );
  expect(screen.queryByText("Facts")).not.toBeInTheDocument();
});

test("shows a loading indicator while fetching", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(<AnswerFactInterpretationScreen bearerToken="token" answerId="answer-3" />);

  expect(screen.getByText("Loading answer...")).toBeInTheDocument();

  resolveFetch({ ok: true, json: async () => ({ facts: [], interpretations: [], no_basis: false }) });

  await waitFor(() => expect(screen.queryByText("Loading answer...")).not.toBeInTheDocument());
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockResolvedValue({
    ok: false,
    json: async () => ({ message: "Answer not found." }),
  });

  render(<AnswerFactInterpretationScreen bearerToken="token" answerId="answer-4" />);

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(await screen.findByRole("alert")).toHaveTextContent("Answer not found.");
});
