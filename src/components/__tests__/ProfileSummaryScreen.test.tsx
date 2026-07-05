import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { ProfileSummaryScreen } from "../ProfileSummaryScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("fetches and renders profile summary recommendations", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      status: "success",
      profile_summary: "Profile summary text.",
      missing_fields: ["motivations"],
      recommendations: ["science-track", "arts-track"],
    }),
  });

  render(<ProfileSummaryScreen bearerToken="token" />);

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByText("Profile summary text.")).toBeInTheDocument();
  expect(screen.getByText("motivations")).toBeInTheDocument();
  expect(screen.getByText("science-track")).toBeInTheDocument();
  expect(screen.getByText("arts-track")).toBeInTheDocument();
});

test("shows fallback when no recommendations are returned", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      status: "success",
      profile_summary: "Profile summary text.",
      missing_fields: [],
      recommendations: [],
    }),
  });

  render(<ProfileSummaryScreen bearerToken="token" />);

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByText("No recommendations available yet.")).toBeInTheDocument();
});

test("shows an auth error when no token is present", async () => {
  render(<ProfileSummaryScreen bearerToken={null} />);

  expect(
    await screen.findByText("You must be signed in to view the profile summary."),
  ).toBeInTheDocument();
});
