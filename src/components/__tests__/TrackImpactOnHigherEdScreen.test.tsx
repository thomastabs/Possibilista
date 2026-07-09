import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { TrackImpactOnHigherEdScreen } from "../TrackImpactOnHigherEdScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("shows a loading indicator while fetching higher education impact", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(<TrackImpactOnHigherEdScreen trackId="track-1" bearerToken="token" />);

  expect(screen.getByText("Loading higher education impact...")).toBeInTheDocument();

  resolveFetch({
    ok: true,
    json: async () => ({ valid: true, impact_description: "", message: "" }),
  });

  await waitFor(() =>
    expect(screen.queryByText("Loading higher education impact...")).not.toBeInTheDocument(),
  );
});

test("fetches and displays the impact description for a valid track", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      valid: true,
      impact_description: "Opens access to STEM higher education courses.",
      message: "Higher education impact retrieved successfully.",
    }),
  });

  render(<TrackImpactOnHigherEdScreen trackId="track-1" bearerToken="token" />);

  await waitFor(() =>
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/secondary-tracks/track-1/higher-ed-impact",
      { headers: { Authorization: "Bearer token" } },
    ),
  );

  expect(
    await screen.findByText("Opens access to STEM higher education courses."),
  ).toBeInTheDocument();
});

test("displays an informative message when the track is invalid or not recognized", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      valid: false,
      impact_description: "",
      message:
        "The track is not recognized, and no impact information is available for the track.",
    }),
  });

  render(<TrackImpactOnHigherEdScreen trackId="unknown-track" />);

  expect(
    await screen.findByText(
      "The track is not recognized, and no impact information is available for the track.",
    ),
  ).toBeInTheDocument();
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockRejectedValue(new Error("Network error"));

  render(<TrackImpactOnHigherEdScreen trackId="track-1" />);

  expect(await screen.findByRole("alert")).toHaveTextContent("Network error");
});

test("includes a back control that triggers onBack", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ valid: true, impact_description: "", message: "" }),
  });
  const onBack = jest.fn();

  render(<TrackImpactOnHigherEdScreen trackId="track-1" onBack={onBack} />);

  fireEvent.click(screen.getByRole("button", { name: "Back to secondary tracks" }));

  expect(onBack).toHaveBeenCalledTimes(1);
});
