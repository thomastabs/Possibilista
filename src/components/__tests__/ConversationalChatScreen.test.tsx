import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { ConversationalChatScreen } from "../ConversationalChatScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("sends a question and displays facts separated from interpretations", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      answer: "According to the official documents 'Professional Courses Guidance', ...",
      facts: ["Professional Courses Guidance (https://www.dge.mec.pt/cursos-profissionais): ..."],
      interpretations: [],
      insufficient_info: false,
      requires_confirmation: false,
      session_id: "session-1",
    }),
  });

  render(<ConversationalChatScreen bearerToken="token" sessionId="session-1" />);

  fireEvent.change(screen.getByLabelText("Your message"), {
    target: { value: "What are the professional tracks?" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByText("Facts")).toBeInTheDocument();
  expect(
    screen.getByText("Professional Courses Guidance (https://www.dge.mec.pt/cursos-profissionais): ..."),
  ).toBeInTheDocument();
  expect(screen.queryByText("Interpretation")).not.toBeInTheDocument();
});

test("renders a compound question's answer as separate, clearly addressed parts", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      answer:
        "1) According to the official documents 'Professional Courses Guidance', ... " +
        "2) According to the official documents 'Specialized Artistic Courses Guidance', ...",
      facts: [
        "Professional Courses Guidance (https://www.dge.mec.pt/cursos-profissionais): ...",
        "Specialized Artistic Courses Guidance (https://www.dge.mec.pt/cursos-artisticos-especializados): ...",
      ],
      interpretations: [],
      insufficient_info: false,
      requires_confirmation: false,
      session_id: "session-9",
    }),
  });

  render(<ConversationalChatScreen bearerToken="token" sessionId="session-9" />);

  fireEvent.change(screen.getByLabelText("Your message"), {
    target: {
      value: "What are the professional tracks? What are the specialized artistic tracks?",
    },
  });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(
    screen.getByText("According to the official documents 'Professional Courses Guidance', ..."),
  ).toBeInTheDocument();
  expect(
    screen.getByText(
      "According to the official documents 'Specialized Artistic Courses Guidance', ...",
    ),
  ).toBeInTheDocument();
  expect(screen.getByText("Facts")).toBeInTheDocument();
});

test("labels interpretation answers distinctly from facts", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      answer: "Based on the general guidance, here is an interpretation, not a direct quote.",
      facts: [],
      interpretations: [
        "This is an interpretation based on general guidance, not a direct quote from official sources.",
      ],
      insufficient_info: false,
      requires_confirmation: false,
      session_id: "session-2",
    }),
  });

  render(<ConversationalChatScreen bearerToken="token" sessionId="session-2" />);

  fireEvent.change(screen.getByLabelText("Your message"), {
    target: { value: "Which track would you recommend for me?" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByText("Interpretation")).toBeInTheDocument();
  expect(
    screen.getByText(
      "This is an interpretation based on general guidance, not a direct quote from official sources.",
    ),
  ).toBeInTheDocument();
  expect(screen.queryByText("Facts")).not.toBeInTheDocument();
});

test("shows a notice when information is insufficient", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      answer: "I do not have enough documented information to answer this confidently.",
      facts: [],
      interpretations: [],
      insufficient_info: true,
      requires_confirmation: false,
      session_id: "session-3",
    }),
  });

  render(<ConversationalChatScreen bearerToken="token" sessionId="session-3" />);

  fireEvent.change(screen.getByLabelText("Your message"), {
    target: { value: "What is the weather tomorrow?" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(
    screen.getByRole("status", {
      name: "The system cannot answer this question based on the current official sources.",
    }),
  ).toBeInTheDocument();
});

test("shows an alert when human confirmation is required", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      answer: "This touches a special regime; confirm with the school.",
      facts: [],
      interpretations: [],
      insufficient_info: false,
      requires_confirmation: true,
      session_id: "session-4",
    }),
  });

  render(<ConversationalChatScreen bearerToken="token" sessionId="session-4" />);

  fireEvent.change(screen.getByLabelText("Your message"), {
    target: { value: "I want to request a special regime equivalence." },
  });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(
    screen.getByText("Human or institutional confirmation is recommended for this answer."),
  ).toBeInTheDocument();
});

test("shows the confirmation advisory alongside facts and interpretations without hiding them", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      answer: "Based on general guidance, here is an interpretation about your special case.",
      facts: ["Secondary Education Overview (https://www.dge.mec.pt/ensino-secundario): ..."],
      interpretations: [
        "This is an interpretation based on general guidance, not a direct quote from official sources.",
      ],
      insufficient_info: false,
      requires_confirmation: true,
      session_id: "session-8",
    }),
  });

  render(<ConversationalChatScreen bearerToken="token" sessionId="session-8" />);

  fireEvent.change(screen.getByLabelText("Your message"), {
    target: { value: "My special case needs an exception — which track would you recommend?" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(
    screen.getByText("Human or institutional confirmation is recommended for this answer."),
  ).toBeInTheDocument();
  expect(screen.getByText("Facts")).toBeInTheDocument();
  expect(screen.getByText("Interpretation")).toBeInTheDocument();
  expect(
    screen.getByText("Secondary Education Overview (https://www.dge.mec.pt/ensino-secundario): ..."),
  ).toBeInTheDocument();
  expect(
    screen.getByText(
      "This is an interpretation based on general guidance, not a direct quote from official sources.",
    ),
  ).toBeInTheDocument();
  expect(screen.queryByRole("status")).not.toBeInTheDocument();
});

test("appends multiple turns to the chat history and clears the input", async () => {
  fetchMock
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        answer: "First answer.",
        facts: ["First fact."],
        interpretations: [],
        insufficient_info: false,
        requires_confirmation: false,
        session_id: "session-5",
      }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        answer: "Second answer.",
        facts: ["Second fact."],
        interpretations: [],
        insufficient_info: false,
        requires_confirmation: false,
        session_id: "session-5",
      }),
    });

  render(<ConversationalChatScreen bearerToken="token" sessionId="session-5" />);

  const input = screen.getByLabelText("Your message");

  fireEvent.change(input, { target: { value: "First question?" } });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));
  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  await screen.findByText("First answer.");
  expect(input).toHaveValue("");

  fireEvent.change(input, { target: { value: "Second question?" } });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));
  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  await screen.findByText("Second answer.");

  expect(screen.getByText("First question?")).toBeInTheDocument();
  expect(screen.getByText("Second question?")).toBeInTheDocument();
  expect(screen.getByText("First answer.")).toBeInTheDocument();
  expect(screen.getByText("Second answer.")).toBeInTheDocument();
});

test("shows an error with retry when the request fails", async () => {
  fetchMock
    .mockResolvedValueOnce({
      ok: false,
      json: async () => ({ answer: "Server error." }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        answer: "Recovered answer.",
        facts: [],
        interpretations: [],
        insufficient_info: false,
        requires_confirmation: false,
        session_id: "session-6",
      }),
    });

  render(<ConversationalChatScreen bearerToken="token" sessionId="session-6" />);

  fireEvent.change(screen.getByLabelText("Your message"), {
    target: { value: "Will this fail?" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByText("Server error.")).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Retry" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  await screen.findByText("Recovered answer.");
});

test("shows auth error when no bearer token is present", () => {
  render(<ConversationalChatScreen bearerToken={null} sessionId="session-7" />);

  expect(screen.getByText("Sign in to start the conversation.")).toBeInTheDocument();
  expect(fetchMock).not.toHaveBeenCalled();
});
