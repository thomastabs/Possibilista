import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { ExplorationPathExplanationScreen } from "../ExplorationPathExplanationScreen";

type FetchArgs = Parameters<typeof fetch>;

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("displays the student's interests, motivations, and academic areas in accessible language", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      interests_explanation: "The student is interested in: Robotics.",
      motivations_explanation: "The student is motivated by: Wants to help people.",
      academic_areas_explanation: "The student is strong in Math; and working to improve History.",
      no_data: false,
    }),
  });

  render(
    <ExplorationPathExplanationScreen bearerToken="token" studentSessionId="session-1" />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

  expect(await screen.findByText("The student is interested in: Robotics.")).toBeInTheDocument();
  expect(
    screen.getByText("The student is motivated by: Wants to help people."),
  ).toBeInTheDocument();
  expect(
    screen.getByText("The student is strong in Math; and working to improve History."),
  ).toBeInTheDocument();
  expect(screen.getByText("Interests")).toBeInTheDocument();
  expect(screen.getByText("Motivations")).toBeInTheDocument();
  expect(screen.getByText("Academic areas")).toBeInTheDocument();
});

test("shows a no-data message when the student has not started exploring", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      interests_explanation: "This student has not started exploring yet.",
      motivations_explanation: "This student has not started exploring yet.",
      academic_areas_explanation: "This student has not started exploring yet.",
      no_data: true,
    }),
  });

  render(
    <ExplorationPathExplanationScreen bearerToken="token" studentSessionId="session-2" />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

  expect(await screen.findByRole("status")).toHaveTextContent(
    "This student has not started exploring yet.",
  );
  expect(screen.queryByText("Interests")).not.toBeInTheDocument();
});

test("shows a loading indicator while the request is in flight", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(
    <ExplorationPathExplanationScreen bearerToken="token" studentSessionId="session-3" />,
  );

  expect(screen.getByText("Loading exploration path...")).toBeInTheDocument();

  resolveFetch({
    ok: true,
    json: async () => ({
      interests_explanation: "The student is interested in: Robotics.",
      motivations_explanation: "",
      academic_areas_explanation: "",
      no_data: false,
    }),
  });

  await waitFor(() =>
    expect(screen.queryByText("Loading exploration path...")).not.toBeInTheDocument(),
  );
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockResolvedValue({
    ok: false,
    json: async () => ({ message: "Student session not found." }),
  });

  render(
    <ExplorationPathExplanationScreen bearerToken="token" studentSessionId="session-4" />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(await screen.findByRole("alert")).toHaveTextContent("Student session not found.");
});

test("sends the bearer token and student session id, and refetches on prop change", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      interests_explanation: "The student is interested in: Robotics.",
      motivations_explanation: "",
      academic_areas_explanation: "",
      no_data: false,
    }),
  });

  const { rerender } = render(
    <ExplorationPathExplanationScreen bearerToken="token-1" studentSessionId="session-5" />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  const [firstUrl, firstOptions] = fetchMock.mock.calls[0] as FetchArgs;
  expect(String(firstUrl)).toContain("student_session_id=session-5");
  expect((firstOptions?.headers as Record<string, string>).Authorization).toBe("Bearer token-1");

  rerender(
    <ExplorationPathExplanationScreen bearerToken="token-2" studentSessionId="session-6" />,
  );

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  const [secondUrl, secondOptions] = fetchMock.mock.calls[1] as FetchArgs;
  expect(String(secondUrl)).toContain("student_session_id=session-6");
  expect((secondOptions?.headers as Record<string, string>).Authorization).toBe("Bearer token-2");
});
