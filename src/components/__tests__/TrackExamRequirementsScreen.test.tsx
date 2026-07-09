import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { TrackExamRequirementsScreen } from "../TrackExamRequirementsScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("shows a loading indicator while fetching exam requirements", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(<TrackExamRequirementsScreen trackId="track-1" bearerToken="token" />);

  expect(screen.getByText("Loading exam requirements...")).toBeInTheDocument();

  resolveFetch({
    ok: true,
    json: async () => ({ valid: true, exams: [], message: "Exam requirements retrieved successfully." }),
  });

  await waitFor(() =>
    expect(screen.queryByText("Loading exam requirements...")).not.toBeInTheDocument(),
  );
});

test("fetches and displays exam requirements for a valid track", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      valid: true,
      exams: [
        { name: "Mathematics A", timing: "End of 12th grade" },
        { name: "Physics and Chemistry", timing: "End of 11th grade" },
      ],
      message: "Exam requirements retrieved successfully.",
    }),
  });

  render(<TrackExamRequirementsScreen trackId="track-1" bearerToken="token" />);

  await waitFor(() =>
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/secondary-tracks/track-1/exam-requirements",
      { headers: { Authorization: "Bearer token" } },
    ),
  );

  expect(await screen.findByText("Mathematics A")).toBeInTheDocument();
  expect(screen.getByText("End of 12th grade")).toBeInTheDocument();
  expect(screen.getByText("Physics and Chemistry")).toBeInTheDocument();
  expect(screen.getByText("End of 11th grade")).toBeInTheDocument();
});

test("displays a user-friendly message for an unknown track", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      valid: false,
      exams: [],
      message: "No information is available for that track. Please ask about valid tracks.",
    }),
  });

  render(<TrackExamRequirementsScreen trackId="unknown-track" />);

  expect(
    await screen.findByText(
      "No information is available for that track. Please ask about valid tracks.",
    ),
  ).toBeInTheDocument();
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockRejectedValue(new Error("Network error"));

  render(<TrackExamRequirementsScreen trackId="track-1" />);

  expect(await screen.findByRole("alert")).toHaveTextContent("Network error");
});

test("includes a back control that triggers onBack", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ valid: true, exams: [], message: "Exam requirements retrieved successfully." }),
  });
  const onBack = jest.fn();

  render(<TrackExamRequirementsScreen trackId="track-1" onBack={onBack} />);

  fireEvent.click(screen.getByRole("button", { name: "Back to secondary tracks" }));

  expect(onBack).toHaveBeenCalledTimes(1);
});
