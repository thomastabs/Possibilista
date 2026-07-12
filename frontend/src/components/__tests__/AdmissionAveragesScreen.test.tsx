import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { AdmissionAveragesScreen } from "../AdmissionAveragesScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("shows a loading indicator while fetching admission averages", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(<AdmissionAveragesScreen courseId="course-1" bearerToken="token" />);

  expect(screen.getByText("Loading admission averages...")).toBeInTheDocument();

  resolveFetch({
    ok: true,
    json: async () => ({ available: true, admission_average: null, exam_weights: [], message: "" }),
  });

  await waitFor(() =>
    expect(screen.queryByText("Loading admission averages...")).not.toBeInTheDocument(),
  );
});

test("displays the admission average and each entrance exam's weight", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      available: true,
      admission_average: 16.5,
      exam_weights: [
        { exam_name: "Mathematics A", weight: 0.4 },
        { exam_name: "Physics and Chemistry", weight: 0.6 },
      ],
      message: "",
    }),
  });

  render(<AdmissionAveragesScreen courseId="course-1" bearerToken="token" />);

  await waitFor(() =>
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/higher-ed/courses/course-1/admission-averages",
      { headers: { Authorization: "Bearer token" } },
    ),
  );

  expect(await screen.findByText("Admission average: 16.50")).toBeInTheDocument();
  expect(screen.getByText("Mathematics A")).toBeInTheDocument();
  expect(screen.getByText("40%")).toBeInTheDocument();
  expect(screen.getByText("Physics and Chemistry")).toBeInTheDocument();
  expect(screen.getByText("60%")).toBeInTheDocument();
});

test("displays a notification when admission criteria data is not available", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      available: false,
      admission_average: null,
      exam_weights: [],
      message: "Admission criteria information is not available for the selected course.",
    }),
  });

  render(<AdmissionAveragesScreen courseId="course-1" bearerToken="token" />);

  expect(
    await screen.findByText(
      "Admission criteria information is not available for the selected course.",
    ),
  ).toBeInTheDocument();
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockRejectedValue(new Error("Network error"));

  render(<AdmissionAveragesScreen courseId="course-1" bearerToken="token" />);

  expect(await screen.findByRole("alert")).toHaveTextContent("Network error");
});
