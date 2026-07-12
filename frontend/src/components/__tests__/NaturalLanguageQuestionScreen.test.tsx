import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { NaturalLanguageQuestionScreen } from "../NaturalLanguageQuestionScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("submits a clear question and shows official documents", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      answer: "According to the official documents, there are three main pathways.",
      clarification_needed: false,
      clarification_options: [],
      out_of_scope: false,
      suggestion: "",
      session_id: "session-1",
      documents: [
        {
          title: "Professional Courses Guidance",
          content: "Professional courses combine general and technical training.",
          source_url: "https://www.dge.mec.pt/cursos-profissionais",
        },
      ],
      no_source: false,
    }),
  });

  render(
    <NaturalLanguageQuestionScreen bearerToken="token" sessionId="session-1" />,
  );

  fireEvent.change(screen.getByLabelText("Your question"), {
    target: { value: "What are the available secondary tracks?" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Ask question" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByText(/According to the official documents/i)).toBeInTheDocument();
  expect(screen.getByText("Professional Courses Guidance")).toBeInTheDocument();
  expect(screen.getByText("Professional courses combine general and technical training.")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Open source" })).toHaveAttribute(
    "href",
    "https://www.dge.mec.pt/cursos-profissionais",
  );
});

test("shows clarification options for an ambiguous question", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      answer: "Your question is a bit broad.",
      clarification_needed: true,
      clarification_options: ["Scientific-humanistic tracks", "Professional tracks"],
      out_of_scope: false,
      suggestion: "Select the track or topic you want me to clarify.",
      session_id: "session-2",
      documents: [],
      no_source: true,
    }),
  });

  render(
    <NaturalLanguageQuestionScreen bearerToken="token" sessionId="session-2" />,
  );

  fireEvent.change(screen.getByLabelText("Your question"), {
    target: { value: "Tell me about secondary education." },
  });
  fireEvent.click(screen.getByRole("button", { name: "Ask question" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByText("Clarification needed")).toBeInTheDocument();
  expect(screen.getByText("Scientific-humanistic tracks")).toBeInTheDocument();
  expect(screen.getByText("Professional tracks")).toBeInTheDocument();
});

test("shows out-of-scope guidance for unrelated questions", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      answer: "I can only answer questions about Portuguese secondary education tracks.",
      clarification_needed: false,
      clarification_options: [],
      out_of_scope: true,
      suggestion: "Please consult a human advisor or school guidance counselor.",
      session_id: "session-3",
      documents: [],
      no_source: true,
    }),
  });

  render(
    <NaturalLanguageQuestionScreen bearerToken="token" sessionId="session-3" />,
  );

  fireEvent.change(screen.getByLabelText("Your question"), {
    target: { value: "What is the weather tomorrow?" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Ask question" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByText("Out of scope")).toBeInTheDocument();
  expect(screen.getByText(/consult a human advisor/i)).toBeInTheDocument();
});

test("shows auth error when no bearer token is present", () => {
  render(<NaturalLanguageQuestionScreen bearerToken={null} sessionId="session-4" />);

  expect(screen.getByText("Sign in to ask a question.")).toBeInTheDocument();
  expect(fetchMock).not.toHaveBeenCalled();
});

test("selecting a clarification option resubmits it as the question", async () => {
  fetchMock
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        answer: "Your question is a bit broad.",
        clarification_needed: true,
        clarification_options: ["Scientific-humanistic tracks", "Professional tracks"],
        out_of_scope: false,
        suggestion: "Select the track or topic you want me to clarify.",
        session_id: "session-5",
        documents: [],
        no_source: true,
      }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        answer: "Scientific-humanistic tracks prepare students for higher education.",
        clarification_needed: false,
        clarification_options: [],
        out_of_scope: false,
        suggestion: "",
        session_id: "session-5",
        documents: [],
        no_source: false,
      }),
    });

  render(
    <NaturalLanguageQuestionScreen bearerToken="token" sessionId="session-5" />,
  );

  fireEvent.change(screen.getByLabelText("Your question"), {
    target: { value: "Tell me about secondary education." },
  });
  fireEvent.click(screen.getByRole("button", { name: "Ask question" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  const optionButton = await screen.findByRole("button", { name: "Scientific-humanistic tracks" });
  fireEvent.click(optionButton);

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  const secondCallBody = JSON.parse(fetchMock.mock.calls[1][1].body);
  expect(secondCallBody).toEqual({
    question: "Scientific-humanistic tracks",
    session_id: "session-5",
  });
  expect(
    await screen.findByText("Scientific-humanistic tracks prepare students for higher education."),
  ).toBeInTheDocument();
});

test("dismissing the out-of-scope message returns to the question input", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      answer: "I can only answer questions about Portuguese secondary education tracks.",
      clarification_needed: false,
      clarification_options: [],
      out_of_scope: true,
      suggestion: "Please consult a human advisor or school guidance counselor.",
      session_id: "session-6",
      documents: [],
      no_source: true,
    }),
  });

  render(
    <NaturalLanguageQuestionScreen bearerToken="token" sessionId="session-6" />,
  );

  fireEvent.change(screen.getByLabelText("Your question"), {
    target: { value: "What is the weather tomorrow?" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Ask question" }));

  await waitFor(() => expect(screen.getByText("Out of scope")).toBeInTheDocument());

  fireEvent.click(screen.getByRole("button", { name: "Ask a new question" }));

  expect(screen.queryByText("Out of scope")).not.toBeInTheDocument();
  expect(screen.getByLabelText("Your question")).toHaveValue("");
});
