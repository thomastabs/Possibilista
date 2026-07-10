import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { SchoolYearInputScreen } from "../SchoolYearInputScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("submits a valid school year and proceeds", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ valid: true, message: "School year accepted." }),
  });
  const onContinue = jest.fn();

  render(
    <SchoolYearInputScreen bearerToken="token" sessionId="session-1" onContinue={onContinue} />,
  );

  fireEvent.change(screen.getByLabelText("School year"), { target: { value: "10" } });
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  const body = JSON.parse(fetchMock.mock.calls[0][1].body);
  expect(body).toEqual({ session_id: "session-1", school_year: 10 });
  expect(fetchMock.mock.calls[0][1].headers.Authorization).toBe("Bearer token");

  expect(await screen.findByText("School year accepted.")).toBeInTheDocument();
  expect(onContinue).toHaveBeenCalledTimes(1);
});

test("displays the backend's error message for an invalid school year and does not proceed", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      valid: false,
      message: "Please provide a valid school year between 9 and 12.",
    }),
  });
  const onContinue = jest.fn();

  render(
    <SchoolYearInputScreen bearerToken="token" sessionId="session-1" onContinue={onContinue} />,
  );

  fireEvent.change(screen.getByLabelText("School year"), { target: { value: "9" } });
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  expect(
    await screen.findByText("Please provide a valid school year between 9 and 12."),
  ).toBeInTheDocument();
  expect(onContinue).not.toHaveBeenCalled();
});

test("shows a loading indicator and disables the submit button while saving", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(<SchoolYearInputScreen bearerToken="token" sessionId="session-1" />);

  fireEvent.change(screen.getByLabelText("School year"), { target: { value: "11" } });
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  expect(screen.getByRole("button", { name: "Saving..." })).toBeDisabled();

  resolveFetch({
    ok: true,
    json: async () => ({ valid: true, message: "School year accepted." }),
  });

  await waitFor(() =>
    expect(screen.queryByRole("button", { name: "Saving..." })).not.toBeInTheDocument(),
  );
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockRejectedValue(new Error("Network error"));

  render(<SchoolYearInputScreen bearerToken="token" sessionId="session-1" />);

  fireEvent.change(screen.getByLabelText("School year"), { target: { value: "12" } });
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  expect(await screen.findByRole("alert")).toHaveTextContent("Network error");
});
