import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { ProfileSummaryScreen } from "../ProfileSummaryScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("shows loading state before the profile summary arrives", () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      status: "success",
      profile_summary: "Profile summary text.",
      missing_fields: [],
      suggestions: [],
    }),
  });

  render(<ProfileSummaryScreen bearerToken="token" />);

  expect(screen.getByText("Loading profile summary...")).toBeInTheDocument();
});

test("fetches and renders profile summary suggestions", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      status: "success",
      profile_summary: "Profile summary text.",
      missing_fields: ["motivations"],
      suggestions: ["Add motivations", "Add academic strengths"],
    }),
  });

  render(<ProfileSummaryScreen bearerToken="token" />);

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByText("Profile summary text.")).toBeInTheDocument();
  expect(screen.getByText("motivations")).toBeInTheDocument();
  expect(screen.getByText("Add motivations")).toBeInTheDocument();
  expect(screen.getByText("Add academic strengths")).toBeInTheDocument();
});

test("falls back to recommendations when suggestions are not returned", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      status: "success",
      profile_summary: "Profile summary text.",
      missing_fields: [],
      recommendations: ["science-track", "arts-track"],
    }),
  });

  render(<ProfileSummaryScreen bearerToken="token" />);

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByText("science-track")).toBeInTheDocument();
  expect(screen.getByText("arts-track")).toBeInTheDocument();
});

test("shows fallback when no suggestions are returned", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      status: "success",
      profile_summary: "Profile summary text.",
      missing_fields: [],
      suggestions: [],
    }),
  });

  render(<ProfileSummaryScreen bearerToken="token" />);

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByText("No suggestions available yet.")).toBeInTheDocument();
  expect(screen.getByText("All required inputs are available.")).toBeInTheDocument();
});

test("shows an error when the backend request fails", async () => {
  fetchMock.mockResolvedValue({
    ok: false,
    json: async () => ({
      message: "Unable to load profile summary.",
    }),
  });

  render(<ProfileSummaryScreen bearerToken="token" />);

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByRole("alert")).toHaveTextContent("Unable to load profile summary.");
});

test("shows an auth error when no token is present", async () => {
  render(<ProfileSummaryScreen bearerToken={null} />);

  expect(
    await screen.findByText("You must be signed in to view the profile summary."),
  ).toBeInTheDocument();
});
