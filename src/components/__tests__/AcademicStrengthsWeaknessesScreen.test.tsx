import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { AcademicStrengthsWeaknessesScreen } from "../AcademicStrengthsWeaknessesScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("renders form fields and supports partial toggle", () => {
  render(
    <AcademicStrengthsWeaknessesScreen bearerToken="token" schoolYear={9} onNavigate={jest.fn()} />,
  );

  expect(screen.getByLabelText("Strengths")).toBeInTheDocument();
  expect(screen.getByLabelText("Weaknesses")).toBeInTheDocument();
  expect(screen.getByLabelText("Partial information")).toBeInTheDocument();
});

test("submits strengths and weaknesses and navigates on recommendation response", async () => {
  const onNavigate = jest.fn();
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      status: "success",
      message: "Academic strengths and weaknesses saved successfully. Recommended tracks: science-track",
    }),
  });

  render(
    <AcademicStrengthsWeaknessesScreen
      bearerToken="token"
      schoolYear={9}
      onNavigate={onNavigate}
      nextPath="/profile-summary"
    />,
  );

  fireEvent.change(screen.getByLabelText("Strengths"), { target: { value: "Math" } });
  fireEvent.click(screen.getByRole("button", { name: "Add strength" }));
  fireEvent.change(screen.getByLabelText("Weaknesses"), { target: { value: "History" } });
  fireEvent.click(screen.getByRole("button", { name: "Add weakness" }));
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/v1/profiling/strengths-weaknesses",
    expect.objectContaining({
      method: "POST",
      headers: expect.objectContaining({
        Authorization: "Bearer token",
        "Content-Type": "application/json",
      }),
      body: JSON.stringify({ strengths: ["Math"], weaknesses: ["History"], partial: false }),
    }),
  );
  expect(onNavigate).toHaveBeenCalledWith("/profile-summary");
});

test("shows clarification message and keeps user on page", async () => {
  const onNavigate = jest.fn();
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      status: "success",
      message: "Clarification needed: please provide more detail.",
    }),
  });

  render(
    <AcademicStrengthsWeaknessesScreen bearerToken="token" schoolYear={9} onNavigate={onNavigate} />,
  );

  fireEvent.click(screen.getByLabelText("Partial information"));
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByText(/clarification needed/i)).toBeInTheDocument();
  expect(onNavigate).not.toHaveBeenCalled();
});

test("allows partial submission with empty lists", async () => {
  const onNavigate = jest.fn();
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      status: "success",
      message: "Academic strengths and weaknesses saved with partial input.",
    }),
  });

  render(
    <AcademicStrengthsWeaknessesScreen bearerToken="token" schoolYear={9} onNavigate={onNavigate} />,
  );

  fireEvent.click(screen.getByLabelText("Partial information"));
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/v1/profiling/strengths-weaknesses",
    expect.objectContaining({
      body: JSON.stringify({ strengths: [], weaknesses: [], partial: true }),
    }),
  );
  expect(onNavigate).toHaveBeenCalledWith("/profile-summary");
});

test("blocks non-9th grade students", () => {
  render(<AcademicStrengthsWeaknessesScreen bearerToken="token" schoolYear={10} />);

  expect(screen.getByText("This screen is only available to 9.º ano students.")).toBeInTheDocument();
});
