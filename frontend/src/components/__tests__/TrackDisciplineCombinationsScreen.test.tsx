import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { TrackDisciplineCombinationsScreen } from "../TrackDisciplineCombinationsScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("shows a loading indicator while fetching discipline combinations", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(<TrackDisciplineCombinationsScreen trackId="track-1" bearerToken="token" />);

  expect(screen.getByText("Loading discipline combinations...")).toBeInTheDocument();

  resolveFetch({
    ok: true,
    json: async () => ({
      valid: true,
      trienais: [],
      bienais: [],
      anuais: [],
      combinations: [],
      message: "",
    }),
  });

  await waitFor(() =>
    expect(screen.queryByText("Loading discipline combinations...")).not.toBeInTheDocument(),
  );
});

test("fetches and displays trienais, bienais, anuais disciplines and valid combinations", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      valid: true,
      trienais: ["Mathematics A"],
      bienais: ["Biology"],
      anuais: ["Philosophy"],
      combinations: ["Mathematics A + Biology"],
      message: "",
    }),
  });

  render(<TrackDisciplineCombinationsScreen trackId="track-1" bearerToken="token" />);

  await waitFor(() =>
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/secondary-tracks/track-1/discipline-combinations",
      { headers: { Authorization: "Bearer token" } },
    ),
  );

  expect(await screen.findByText("Mathematics A")).toBeInTheDocument();
  expect(screen.getByText("Biology")).toBeInTheDocument();
  expect(screen.getByText("Philosophy")).toBeInTheDocument();
  expect(screen.getByText("Mathematics A + Biology")).toBeInTheDocument();
});

test("displays the message when no valid combinations exist", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      valid: false,
      trienais: [],
      bienais: [],
      anuais: [],
      combinations: [],
      message: "There are no valid discipline combinations for this track.",
    }),
  });

  render(<TrackDisciplineCombinationsScreen trackId="track-1" />);

  expect(
    await screen.findByText("There are no valid discipline combinations for this track."),
  ).toBeInTheDocument();
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockRejectedValue(new Error("Network error"));

  render(<TrackDisciplineCombinationsScreen trackId="track-1" />);

  expect(await screen.findByRole("alert")).toHaveTextContent("Network error");
});

test("includes a back control that triggers onBack", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      valid: true,
      trienais: [],
      bienais: [],
      anuais: [],
      combinations: [],
      message: "",
    }),
  });
  const onBack = jest.fn();

  render(<TrackDisciplineCombinationsScreen trackId="track-1" onBack={onBack} />);

  fireEvent.click(screen.getByRole("button", { name: "Back to secondary tracks" }));

  expect(onBack).toHaveBeenCalledTimes(1);
});
