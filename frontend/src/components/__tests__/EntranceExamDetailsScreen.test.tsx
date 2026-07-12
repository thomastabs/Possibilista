import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { EntranceExamDetailsScreen } from "../EntranceExamDetailsScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("shows a loading indicator while fetching entrance exam requirements", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(<EntranceExamDetailsScreen courseId="course-1" bearerToken="token" />);

  expect(screen.getByText("Loading entrance exam requirements...")).toBeInTheDocument();

  resolveFetch({
    ok: true,
    json: async () => ({ available: true, exams: [], message: "" }),
  });

  await waitFor(() =>
    expect(screen.queryByText("Loading entrance exam requirements...")).not.toBeInTheDocument(),
  );
});

test("displays the required entrance exams and their weights for a valid course", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      available: true,
      exams: [
        { name: "Mathematics A", weight: 0.4 },
        { name: "Physics and Chemistry", weight: 0.6 },
      ],
      message: "",
    }),
  });

  render(<EntranceExamDetailsScreen courseId="course-1" bearerToken="token" />);

  await waitFor(() =>
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/higher-ed/courses/course-1/entrance-exams",
      { headers: { Authorization: "Bearer token" } },
    ),
  );

  expect(await screen.findByText("Mathematics A")).toBeInTheDocument();
  expect(screen.getByText("40%")).toBeInTheDocument();
  expect(screen.getByText("Physics and Chemistry")).toBeInTheDocument();
  expect(screen.getByText("60%")).toBeInTheDocument();
});

test("displays an unavailable info message for a course not in the system", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      available: false,
      exams: [],
      message: "Exam requirements are unavailable for the selected course.",
    }),
  });

  render(<EntranceExamDetailsScreen courseId="unknown-course" />);

  expect(
    await screen.findByText("Exam requirements are unavailable for the selected course."),
  ).toBeInTheDocument();
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockRejectedValue(new Error("Network error"));

  render(<EntranceExamDetailsScreen courseId="course-1" />);

  expect(await screen.findByRole("alert")).toHaveTextContent("Network error");
});
