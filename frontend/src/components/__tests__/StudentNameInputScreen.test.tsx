import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { StudentNameInputScreen } from "../StudentNameInputScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("submits the provided name and shows the acknowledgment message", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      status: "success",
      message: "Thanks, Maria! We'll use your name for this session.",
    }),
  });
  const onContinue = jest.fn();

  render(
    <StudentNameInputScreen
      bearerToken="token"
      sessionId="session-1"
      onContinue={onContinue}
    />,
  );

  fireEvent.change(screen.getByLabelText("Your name"), { target: { value: "Maria" } });
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  const body = JSON.parse(fetchMock.mock.calls[0][1].body);
  expect(body).toEqual({ session_id: "session-1", name: "Maria", skipped: false });
  expect(fetchMock.mock.calls[0][1].headers.Authorization).toBe("Bearer token");

  expect(
    await screen.findByText("Thanks, Maria! We'll use your name for this session."),
  ).toBeInTheDocument();
  expect(onContinue).toHaveBeenCalledTimes(1);
});

test("skips name entry and continues without personalization", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ status: "success", message: "Continuing without personalization." }),
  });
  const onContinue = jest.fn();

  render(
    <StudentNameInputScreen
      bearerToken="token"
      sessionId="session-1"
      onContinue={onContinue}
    />,
  );

  fireEvent.click(screen.getByRole("button", { name: "Skip" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  const body = JSON.parse(fetchMock.mock.calls[0][1].body);
  expect(body).toEqual({ session_id: "session-1", skipped: true });

  expect(await screen.findByText("Continuing without personalization.")).toBeInTheDocument();
  expect(onContinue).toHaveBeenCalledTimes(1);
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockResolvedValue({
    ok: false,
    json: async () => ({ status: "error", message: "Unable to save your name." }),
  });

  render(<StudentNameInputScreen bearerToken="token" sessionId="session-1" />);

  fireEvent.change(screen.getByLabelText("Your name"), { target: { value: "Maria" } });
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  expect(await screen.findByRole("alert")).toHaveTextContent("Unable to save your name.");
});
