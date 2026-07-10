import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { AgeInputScreen } from "../AgeInputScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("submits a valid age and proceeds without showing an error", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ valid: true, message: "Age accepted." }),
  });
  const onContinue = jest.fn();

  render(<AgeInputScreen bearerToken="token" sessionId="session-1" onContinue={onContinue} />);

  fireEvent.change(screen.getByLabelText("Your age"), { target: { value: "10" } });
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  const body = JSON.parse(fetchMock.mock.calls[0][1].body);
  expect(body).toEqual({ session_id: "session-1", age: 10 });
  expect(fetchMock.mock.calls[0][1].headers.Authorization).toBe("Bearer token");

  expect(await screen.findByText("Age accepted.")).toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  expect(onContinue).toHaveBeenCalledTimes(1);
});

test("displays the backend's error message for an age outside the valid range and allows retry", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      valid: false,
      message: "Please provide a valid age between 9 and 12.",
    }),
  });
  const onContinue = jest.fn();

  render(<AgeInputScreen bearerToken="token" sessionId="session-1" onContinue={onContinue} />);

  const input = screen.getByLabelText("Your age");
  fireEvent.change(input, { target: { value: "20" } });
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  expect(
    await screen.findByText("Please provide a valid age between 9 and 12."),
  ).toBeInTheDocument();
  expect(onContinue).not.toHaveBeenCalled();
  expect(input).not.toBeDisabled();
});

test("clears the error message when the age input is modified", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      valid: false,
      message: "Please provide a valid age between 9 and 12.",
    }),
  });

  render(<AgeInputScreen bearerToken="token" sessionId="session-1" />);

  const input = screen.getByLabelText("Your age");
  fireEvent.change(input, { target: { value: "20" } });
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  expect(
    await screen.findByText("Please provide a valid age between 9 and 12."),
  ).toBeInTheDocument();

  fireEvent.change(input, { target: { value: "10" } });

  expect(
    screen.queryByText("Please provide a valid age between 9 and 12."),
  ).not.toBeInTheDocument();
});

test("shows a loading indicator while saving", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(<AgeInputScreen bearerToken="token" sessionId="session-1" />);

  fireEvent.change(screen.getByLabelText("Your age"), { target: { value: "11" } });
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  expect(screen.getByRole("button", { name: "Saving..." })).toBeDisabled();

  resolveFetch({
    ok: true,
    json: async () => ({ valid: true, message: "Age accepted." }),
  });

  await waitFor(() =>
    expect(screen.queryByRole("button", { name: "Saving..." })).not.toBeInTheDocument(),
  );
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockRejectedValue(new Error("Network error"));

  render(<AgeInputScreen bearerToken="token" sessionId="session-1" />);

  fireEvent.change(screen.getByLabelText("Your age"), { target: { value: "10" } });
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  expect(await screen.findByRole("alert")).toHaveTextContent("Network error");
});
