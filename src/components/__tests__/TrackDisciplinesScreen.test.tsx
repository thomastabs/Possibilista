import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { TrackDisciplinesScreen } from "../TrackDisciplinesScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("shows a loading indicator while fetching disciplines", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(<TrackDisciplinesScreen trackId="track-1" bearerToken="token" />);

  expect(screen.getByText("Loading disciplines...")).toBeInTheDocument();

  resolveFetch({
    ok: true,
    json: async () => ({ valid: true, disciplines: [], message: "Disciplines retrieved successfully." }),
  });

  await waitFor(() => expect(screen.queryByText("Loading disciplines...")).not.toBeInTheDocument());
});

test("fetches and displays disciplines for a valid track", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      valid: true,
      disciplines: ["Mathematics", "Physics"],
      message: "Disciplines retrieved successfully.",
    }),
  });

  render(<TrackDisciplinesScreen trackId="track-1" bearerToken="token" />);

  await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
    "/api/v1/secondary-tracks/track-1/disciplines",
    { headers: { Authorization: "Bearer token" } },
  ));

  expect(await screen.findByText("Mathematics")).toBeInTheDocument();
  expect(screen.getByText("Physics")).toBeInTheDocument();
});

test("displays an invalid track message for an unknown track", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      valid: false,
      disciplines: [],
      message: "The specified secondary track does not exist. Please ask about valid tracks.",
    }),
  });

  render(<TrackDisciplinesScreen trackId="unknown-track" />);

  expect(
    await screen.findByText(
      "The specified secondary track does not exist. Please ask about valid tracks.",
    ),
  ).toBeInTheDocument();
  expect(screen.getByText("Please ask about one of the valid secondary tracks.")).toBeInTheDocument();
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockRejectedValue(new Error("Network error"));

  render(<TrackDisciplinesScreen trackId="track-1" />);

  expect(await screen.findByRole("alert")).toHaveTextContent("Network error");
});

test("includes a control to navigate back to the secondary tracks list", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ valid: true, disciplines: [], message: "Disciplines retrieved successfully." }),
  });
  const onBack = jest.fn();

  render(<TrackDisciplinesScreen trackId="track-1" onBack={onBack} />);

  fireEvent.click(screen.getByRole("button", { name: "Back to secondary tracks" }));

  expect(onBack).toHaveBeenCalledTimes(1);
});
