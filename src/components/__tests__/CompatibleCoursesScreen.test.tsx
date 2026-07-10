import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { CompatibleCoursesScreen } from "../CompatibleCoursesScreen";

const fetchMock = jest.fn();
const VALID_TRACK_ID = "11111111-1111-1111-1111-111111111111";

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("shows a loading indicator while fetching compatible courses", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(<CompatibleCoursesScreen trackId={VALID_TRACK_ID} bearerToken="token" />);

  expect(screen.getByText("Loading compatible courses...")).toBeInTheDocument();

  resolveFetch({
    ok: true,
    json: async () => ({ courses: [], message: "" }),
  });

  await waitFor(() =>
    expect(screen.queryByText("Loading compatible courses...")).not.toBeInTheDocument(),
  );
});

test("fetches with the correct secondary_track_id and displays compatible courses", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      courses: [
        { id: "course-1", name: "Computer Science" },
        { id: "course-2", name: "Mechanical Engineering" },
      ],
      message: "",
    }),
  });

  render(<CompatibleCoursesScreen trackId={VALID_TRACK_ID} bearerToken="token" />);

  await waitFor(() =>
    expect(fetchMock).toHaveBeenCalledWith(
      `/api/v1/higher-ed/courses?secondary_track_id=${VALID_TRACK_ID}`,
      { headers: { Authorization: "Bearer token" } },
    ),
  );

  expect(await screen.findByText("Computer Science")).toBeInTheDocument();
  expect(screen.getByText("Mechanical Engineering")).toBeInTheDocument();
});

test("displays the backend's no-data message for an unsupported track", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      courses: [],
      message: "No data is available for the entered secondary track.",
    }),
  });

  render(<CompatibleCoursesScreen trackId={VALID_TRACK_ID} />);

  expect(
    await screen.findByText("No data is available for the entered secondary track."),
  ).toBeInTheDocument();
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockRejectedValue(new Error("Network error"));

  render(<CompatibleCoursesScreen trackId={VALID_TRACK_ID} />);

  expect(await screen.findByRole("alert")).toHaveTextContent("Network error");
});
