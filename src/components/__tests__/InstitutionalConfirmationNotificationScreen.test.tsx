import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { InstitutionalConfirmationNotificationScreen } from "../InstitutionalConfirmationNotificationScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("displays the alert message when an institutional confirmation alert is present", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      alert_present: true,
      alert_message:
        "Certain academic choices require confirmation from official institutions.",
    }),
  });

  render(
    <InstitutionalConfirmationNotificationScreen
      bearerToken="token"
      studentSessionId="session-1"
    />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Certain academic choices require confirmation from official institutions.",
  );
});

test("renders nothing when no institutional confirmation alert is present", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      alert_present: false,
      alert_message: "",
    }),
  });

  const { container } = render(
    <InstitutionalConfirmationNotificationScreen
      bearerToken="token"
      studentSessionId="session-2"
    />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  await waitFor(() => expect(container).toBeEmptyDOMElement());
});

test("shows a loading indicator while fetching data", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(
    <InstitutionalConfirmationNotificationScreen
      bearerToken="token"
      studentSessionId="session-3"
    />,
  );

  expect(screen.getByText("Checking for confirmation notifications...")).toBeInTheDocument();

  resolveFetch({
    ok: true,
    json: async () => ({ alert_present: false, alert_message: "" }),
  });

  await waitFor(() =>
    expect(
      screen.queryByText("Checking for confirmation notifications..."),
    ).not.toBeInTheDocument(),
  );
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockResolvedValue({
    ok: false,
    json: async () => ({ message: "Student session not found." }),
  });

  render(
    <InstitutionalConfirmationNotificationScreen
      bearerToken="token"
      studentSessionId="session-4"
    />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(await screen.findByRole("alert")).toHaveTextContent("Student session not found.");
});

test("sends the bearer token in the Authorization header", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ alert_present: false, alert_message: "" }),
  });

  render(
    <InstitutionalConfirmationNotificationScreen
      bearerToken="my-token"
      studentSessionId="session-5"
    />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  const [, options] = fetchMock.mock.calls[0];
  expect((options.headers as Record<string, string>).Authorization).toBe("Bearer my-token");
});
