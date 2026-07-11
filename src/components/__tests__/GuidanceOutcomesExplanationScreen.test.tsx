import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { GuidanceOutcomesExplanationScreen } from "../GuidanceOutcomesExplanationScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("fetches and displays guidance recommendations with source references", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      recommendations: [
        {
          text: "The Professional Track is a strong match based on the student's academic strengths.",
          source: "https://www.dge.mec.pt/cursos-profissionais",
        },
      ],
      pending: false,
    }),
  });

  render(
    <GuidanceOutcomesExplanationScreen bearerToken="token" studentSessionId="session-1" />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

  expect(
    await screen.findByText(
      "The Professional Track is a strong match based on the student's academic strengths.",
    ),
  ).toBeInTheDocument();
  expect(
    screen.getByText("Source: https://www.dge.mec.pt/cursos-profissionais", { exact: false }),
  ).toBeInTheDocument();
});

test("displays a pending message when no recommendations have been generated", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      recommendations: [],
      pending: true,
    }),
  });

  render(
    <GuidanceOutcomesExplanationScreen bearerToken="token" studentSessionId="session-2" />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

  expect(await screen.findByRole("status")).toHaveTextContent(
    "Guidance is still pending for this student.",
  );
});

test("shows a loading indicator while fetching data", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(
    <GuidanceOutcomesExplanationScreen bearerToken="token" studentSessionId="session-3" />,
  );

  expect(screen.getByText("Loading guidance outcomes...")).toBeInTheDocument();

  resolveFetch({
    ok: true,
    json: async () => ({ recommendations: [], pending: true }),
  });

  await waitFor(() =>
    expect(screen.queryByText("Loading guidance outcomes...")).not.toBeInTheDocument(),
  );
});

test("handles and displays an error message when the request fails", async () => {
  fetchMock.mockResolvedValue({
    ok: false,
    json: async () => ({ message: "Student session not found." }),
  });

  render(
    <GuidanceOutcomesExplanationScreen bearerToken="token" studentSessionId="session-4" />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(await screen.findByRole("alert")).toHaveTextContent("Student session not found.");
});
