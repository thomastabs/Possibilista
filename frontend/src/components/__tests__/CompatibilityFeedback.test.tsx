import React from "react";
import { render, screen } from "@testing-library/react";
import { CompatibilityFeedback } from "../CompatibilityFeedback";

test("informs the student when no compatible higher education courses are found", () => {
  render(
    <CompatibilityFeedback
      compatible={false}
      message="No compatible higher education courses were found for this secondary track."
    />,
  );

  expect(
    screen.getByText(
      "No compatible higher education courses were found for this secondary track.",
    ),
  ).toBeInTheDocument();
});

test("prompts the student to correct or complete their input for invalid or incomplete data", () => {
  render(
    <CompatibilityFeedback
      compatible={false}
      message="Please correct your secondary track input; the track was not recognized."
    />,
  );

  expect(screen.getByRole("alert")).toHaveTextContent(
    "Please correct your secondary track input; the track was not recognized.",
  );
});

test("prompts completion when compatibility data is missing", () => {
  render(
    <CompatibilityFeedback
      compatible={false}
      message="Please complete your secondary track input; no compatibility data is available yet."
    />,
  );

  expect(screen.getByRole("alert")).toHaveTextContent(
    "Please complete your secondary track input; no compatibility data is available yet.",
  );
});

test("renders a positive status when compatible courses exist", () => {
  render(
    <CompatibilityFeedback
      compatible={true}
      message="Compatible higher education courses were found for this secondary track."
    />,
  );

  expect(screen.getByRole("status")).toHaveTextContent(
    "Compatible higher education courses were found for this secondary track.",
  );
});
