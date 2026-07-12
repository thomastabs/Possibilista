import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { SessionEndScreen } from "../SessionEndScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("renders a confirmation prompt", () => {
  render(<SessionEndScreen bearerToken="token" sessionId="session-1" />);

  expect(
    screen.getByText("Are you sure you want to end this session? All stored data will be cleared."),
  ).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Confirm" })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument();
});

test("sends a POST request with the session id and bearer token on confirm", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ status: "success", message: "Session data was cleared." }),
  });

  render(<SessionEndScreen bearerToken="token" sessionId="session-1" />);

  fireEvent.click(screen.getByRole("button", { name: "Confirm" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/v1/session/end",
    expect.objectContaining({
      method: "POST",
      headers: expect.objectContaining({
        Authorization: "Bearer token",
        "Content-Type": "application/json",
      }),
      body: JSON.stringify({ session_id: "session-1" }),
    }),
  );
});

test("displays a confirmation message and invokes onSessionEnded on success", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ status: "success", message: "Session data was cleared." }),
  });
  const onSessionEnded = jest.fn();

  render(
    <SessionEndScreen
      bearerToken="token"
      sessionId="session-1"
      onSessionEnded={onSessionEnded}
    />,
  );

  fireEvent.click(screen.getByRole("button", { name: "Confirm" }));

  expect(await screen.findByText("Session data was cleared.")).toBeInTheDocument();
  expect(onSessionEnded).toHaveBeenCalledTimes(1);
});

test("displays an error message when the request fails", async () => {
  fetchMock.mockResolvedValue({
    ok: false,
    json: async () => ({ status: "error", message: "Unable to end the session." }),
  });

  render(<SessionEndScreen bearerToken="token" sessionId="session-1" />);

  fireEvent.click(screen.getByRole("button", { name: "Confirm" }));

  expect(await screen.findByRole("alert")).toHaveTextContent("Unable to end the session.");
});

test("disables the confirm button while the request is in progress", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(<SessionEndScreen bearerToken="token" sessionId="session-1" />);

  fireEvent.click(screen.getByRole("button", { name: "Confirm" }));

  expect(screen.getByRole("button", { name: "Ending..." })).toBeDisabled();

  resolveFetch({
    ok: true,
    json: async () => ({ status: "success", message: "Session data was cleared." }),
  });

  await waitFor(() =>
    expect(screen.queryByRole("button", { name: "Ending..." })).not.toBeInTheDocument(),
  );
});

test("invokes onCancel when the cancel button is clicked", () => {
  const onCancel = jest.fn();

  render(<SessionEndScreen bearerToken="token" sessionId="session-1" onCancel={onCancel} />);

  fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

  expect(onCancel).toHaveBeenCalledTimes(1);
  expect(fetchMock).not.toHaveBeenCalled();
});
