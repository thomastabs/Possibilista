import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { SecondaryTrackMemoryPromptScreen } from "../SecondaryTrackMemoryPromptScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("shows a loading indicator while fetching track memory", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(<SecondaryTrackMemoryPromptScreen bearerToken="token" sessionId="session-1" />);

  expect(screen.getByText("Loading secondary track memory...")).toBeInTheDocument();

  resolveFetch({
    ok: true,
    json: async () => ({ track_explored: false, stored_track_id: null, message: "" }),
  });

  await waitFor(() =>
    expect(screen.queryByText("Loading secondary track memory...")).not.toBeInTheDocument(),
  );
});

test("displays the stored track confirmation when a track has been explored", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      track_explored: true,
      stored_track_id: "track-1",
      message: "Continuing with the previously explored secondary track.",
    }),
  });
  const onAskQuestions = jest.fn();

  render(
    <SecondaryTrackMemoryPromptScreen
      bearerToken="token"
      sessionId="session-1"
      onAskQuestions={onAskQuestions}
    />,
  );

  await waitFor(() =>
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/session/secondary-track-memory?session_id=session-1",
      { headers: { Authorization: "Bearer token" } },
    ),
  );

  expect(
    await screen.findByText("Continuing with the previously explored secondary track."),
  ).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Ask follow-up questions" }));
  expect(onAskQuestions).toHaveBeenCalledWith("track-1");
});

test("prompts the student to explore a secondary track when none is stored", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      track_explored: false,
      stored_track_id: null,
      message: "Please explore a secondary track first.",
    }),
  });
  const onExploreTrack = jest.fn();

  render(
    <SecondaryTrackMemoryPromptScreen
      bearerToken="token"
      sessionId="session-1"
      onExploreTrack={onExploreTrack}
    />,
  );

  expect(
    await screen.findByText("Please explore a secondary track first."),
  ).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Explore a secondary track" }));
  expect(onExploreTrack).toHaveBeenCalledTimes(1);
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockRejectedValue(new Error("Network error"));

  render(<SecondaryTrackMemoryPromptScreen bearerToken="token" sessionId="session-1" />);

  expect(await screen.findByRole("alert")).toHaveTextContent("Network error");
});
