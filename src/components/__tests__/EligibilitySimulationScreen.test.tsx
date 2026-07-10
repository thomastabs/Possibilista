import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { EligibilitySimulationScreen } from "../EligibilitySimulationScreen";

const fetchMock = jest.fn();

const TRACK_ID = "11111111-1111-1111-1111-111111111111";

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

const mockTracksResponse = () => ({
  ok: true,
  json: async () => ({
    tracks: [{ id: TRACK_ID, name: "Science and Technology", description: null }],
  }),
});

test("displays eligible courses for a valid secondary track", async () => {
  fetchMock
    .mockResolvedValueOnce(mockTracksResponse())
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        eligible_courses: [
          { id: "course-1", name: "Computer Science" },
          { id: "course-2", name: "Mechanical Engineering" },
        ],
        incomplete_data: false,
        message: "Eligibility simulation completed successfully.",
      }),
    });

  render(<EligibilitySimulationScreen bearerToken="token" />);

  await waitFor(() =>
    expect(screen.getByText("Science and Technology")).toBeInTheDocument(),
  );

  fireEvent.change(screen.getByLabelText("Secondary track"), {
    target: { value: TRACK_ID },
  });
  fireEvent.click(screen.getByRole("button", { name: "Simulate eligibility" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  const secondCallBody = JSON.parse(fetchMock.mock.calls[1][1].body);
  expect(secondCallBody).toEqual({ secondary_track_id: TRACK_ID });
  expect(fetchMock.mock.calls[1][1].headers.Authorization).toBe("Bearer token");

  expect(await screen.findByText("Computer Science")).toBeInTheDocument();
  expect(screen.getByText("Mechanical Engineering")).toBeInTheDocument();
});

test("displays an incomplete-data warning for partial secondary track information", async () => {
  fetchMock
    .mockResolvedValueOnce(mockTracksResponse())
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        eligible_courses: [],
        incomplete_data: true,
        message:
          "Eligibility cannot be fully assessed due to incomplete or missing secondary track data.",
      }),
    });

  render(<EligibilitySimulationScreen bearerToken="token" />);

  await waitFor(() =>
    expect(screen.getByText("Science and Technology")).toBeInTheDocument(),
  );

  fireEvent.change(screen.getByLabelText("Secondary track"), {
    target: { value: TRACK_ID },
  });
  fireEvent.click(screen.getByRole("button", { name: "Simulate eligibility" }));

  expect(
    await screen.findByText(
      "Eligibility cannot be fully assessed due to incomplete or missing secondary track data.",
    ),
  ).toBeInTheDocument();
});

test("shows a loading indicator while simulating eligibility", async () => {
  let resolveSubmit: (value: unknown) => void = () => {};
  fetchMock.mockResolvedValueOnce(mockTracksResponse()).mockReturnValueOnce(
    new Promise((resolve) => {
      resolveSubmit = resolve;
    }),
  );

  render(<EligibilitySimulationScreen bearerToken="token" />);

  await waitFor(() =>
    expect(screen.getByText("Science and Technology")).toBeInTheDocument(),
  );

  fireEvent.change(screen.getByLabelText("Secondary track"), {
    target: { value: TRACK_ID },
  });
  fireEvent.click(screen.getByRole("button", { name: "Simulate eligibility" }));

  expect(screen.getByText("Simulating eligibility...")).toBeInTheDocument();

  resolveSubmit({
    ok: true,
    json: async () => ({ eligible_courses: [], incomplete_data: false, message: "" }),
  });

  await waitFor(() =>
    expect(screen.queryByText("Simulating eligibility...")).not.toBeInTheDocument(),
  );
});

test("shows an error message when the simulation request fails", async () => {
  fetchMock
    .mockResolvedValueOnce(mockTracksResponse())
    .mockRejectedValueOnce(new Error("Network error"));

  render(<EligibilitySimulationScreen bearerToken="token" />);

  await waitFor(() =>
    expect(screen.getByText("Science and Technology")).toBeInTheDocument(),
  );

  fireEvent.change(screen.getByLabelText("Secondary track"), {
    target: { value: TRACK_ID },
  });
  fireEvent.click(screen.getByRole("button", { name: "Simulate eligibility" }));

  expect(await screen.findByRole("alert")).toHaveTextContent("Network error");
});

test("includes back and continue controls", async () => {
  fetchMock
    .mockResolvedValueOnce(mockTracksResponse())
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        eligible_courses: [{ id: "course-1", name: "Computer Science" }],
        incomplete_data: false,
        message: "Eligibility simulation completed successfully.",
      }),
    });
  const onBack = jest.fn();
  const onContinue = jest.fn();

  render(
    <EligibilitySimulationScreen bearerToken="token" onBack={onBack} onContinue={onContinue} />,
  );

  fireEvent.click(screen.getByRole("button", { name: "Back" }));
  expect(onBack).toHaveBeenCalledTimes(1);

  await waitFor(() =>
    expect(screen.getByText("Science and Technology")).toBeInTheDocument(),
  );

  fireEvent.change(screen.getByLabelText("Secondary track"), {
    target: { value: TRACK_ID },
  });
  fireEvent.click(screen.getByRole("button", { name: "Simulate eligibility" }));

  const continueButton = await screen.findByRole("button", { name: "Continue" });
  fireEvent.click(continueButton);
  expect(onContinue).toHaveBeenCalledTimes(1);
});
