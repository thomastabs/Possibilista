import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { InterestPreferencesScreen } from "../InterestPreferencesScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("renders interests and allows multiple selection", () => {
  render(
    <InterestPreferencesScreen
      bearerToken="token"
      sessionId="session-1"
      schoolYear={9}
      interestsQuestions={["Art", "Science"]}
      onNavigate={jest.fn()}
    />,
  );

  expect(screen.getByText("Art")).toBeInTheDocument();
  expect(screen.getByText("Science")).toBeInTheDocument();
});

test("submits selected interests and navigates", async () => {
  const onNavigate = jest.fn();
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ status: "success", message: "Saved" }),
  });

  render(
    <InterestPreferencesScreen
      bearerToken="token"
      sessionId="session-1"
      schoolYear={9}
      interestsQuestions={["Art", "Science"]}
      onNavigate={onNavigate}
    />,
  );

  fireEvent.click(screen.getByLabelText("Art"));
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/v1/session/interests",
    expect.objectContaining({
      method: "POST",
      headers: expect.objectContaining({
        Authorization: "Bearer token",
        "Content-Type": "application/json",
      }),
      body: JSON.stringify({ session_id: "session-1", interests: ["Art"], skipped: false }),
    }),
  );
  expect(onNavigate).toHaveBeenCalledWith("/motivations");
});

test("allows adding a custom interest", async () => {
  const onNavigate = jest.fn();
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ status: "success", message: "Saved" }),
  });

  render(
    <InterestPreferencesScreen
      bearerToken="token"
      sessionId="session-1"
      schoolYear={9}
      onNavigate={onNavigate}
    />,
  );

  fireEvent.change(screen.getByLabelText("Add another interest"), {
    target: { value: "Robotics" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Add" }));
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/v1/session/interests",
    expect.objectContaining({
      body: JSON.stringify({ session_id: "session-1", interests: ["Robotics"], skipped: false }),
    }),
  );
  expect(onNavigate).toHaveBeenCalledWith("/motivations");
});

test("skips interest questions and navigates", async () => {
  const onNavigate = jest.fn();
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ status: "success", message: "Skipped" }),
  });

  render(
    <InterestPreferencesScreen
      bearerToken="token"
      sessionId="session-1"
      schoolYear={9}
      onNavigate={onNavigate}
    />,
  );

  fireEvent.click(screen.getByRole("button", { name: "Skip" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/v1/session/interests",
    expect.objectContaining({
      method: "POST",
      headers: expect.objectContaining({
        Authorization: "Bearer token",
      }),
      body: JSON.stringify({ session_id: "session-1", interests: [], skipped: true }),
    }),
  );
  expect(onNavigate).toHaveBeenCalledWith("/motivations");
});

test("blocks non-9th grade students", () => {
  render(<InterestPreferencesScreen bearerToken="token" sessionId="session-1" schoolYear={10} />);

  expect(screen.getByText("This screen is only available to 9.º ano students.")).toBeInTheDocument();
});

test("shows an error when no session id is provided", async () => {
  render(<InterestPreferencesScreen bearerToken="token" schoolYear={9} />);

  fireEvent.click(screen.getByRole("button", { name: "Skip" }));

  expect(
    await screen.findByText("A session id is required to continue."),
  ).toBeInTheDocument();
  expect(fetchMock).not.toHaveBeenCalled();
});
