import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MotivationsInputScreen } from "../MotivationsInputScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("renders motivations input and buttons", () => {
  render(<MotivationsInputScreen bearerToken="token" schoolYear={9} onNavigate={jest.fn()} />);

  expect(screen.getByLabelText("Your motivations")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Save motivations" })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Decline" })).toBeInTheDocument();
});

test("submits motivations and navigates", async () => {
  const onNavigate = jest.fn();
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ status: "success", message: "Motivations saved successfully." }),
  });

  render(
    <MotivationsInputScreen
      bearerToken="token"
      schoolYear={9}
      onNavigate={onNavigate}
      nextPath="/academic-strengths-weaknesses"
    />,
  );

  fireEvent.change(screen.getByLabelText("Your motivations"), {
    target: { value: "I enjoy solving problems." },
  });
  fireEvent.click(screen.getByRole("button", { name: "Save motivations" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/v1/profiling/motivations",
    expect.objectContaining({
      method: "POST",
      headers: expect.objectContaining({
        Authorization: "Bearer token",
        "Content-Type": "application/json",
      }),
      body: JSON.stringify({ motivations: "I enjoy solving problems.", declined: false }),
    }),
  );
  expect(onNavigate).toHaveBeenCalledWith("/academic-strengths-weaknesses");
});

test("declines motivations and navigates", async () => {
  const onNavigate = jest.fn();
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ status: "success", message: "Motivations declined and recorded." }),
  });

  render(
    <MotivationsInputScreen
      bearerToken="token"
      schoolYear={9}
      onNavigate={onNavigate}
      nextPath="/academic-strengths-weaknesses"
    />,
  );

  fireEvent.click(screen.getByRole("button", { name: "Decline" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/v1/profiling/motivations",
    expect.objectContaining({
      body: JSON.stringify({ motivations: "", declined: true }),
    }),
  );
  expect(onNavigate).toHaveBeenCalledWith("/academic-strengths-weaknesses");
});

test("shows validation error when motivations are empty", () => {
  render(<MotivationsInputScreen bearerToken="token" schoolYear={9} />);

  fireEvent.click(screen.getByRole("button", { name: "Save motivations" }));

  expect(screen.getByText("Enter your motivations or choose to decline.")).toBeInTheDocument();
  expect(fetchMock).not.toHaveBeenCalled();
});

test("blocks non-9th grade students", () => {
  render(<MotivationsInputScreen bearerToken="token" schoolYear={10} />);

  expect(screen.getByText("This screen is only available to 9.º ano students.")).toBeInTheDocument();
});
