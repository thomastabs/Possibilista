import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { DocumentRetrievalScreen } from "../DocumentRetrievalScreen";

const fetchMock = jest.fn();

beforeEach(() => {
  fetchMock.mockReset();
  (global as typeof globalThis).fetch = fetchMock as typeof fetch;
});

test("displays official documents supporting the answer when the query matches indexed documents", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      documents: [
        {
          title: "Professional Courses Guidance",
          content: "Professional courses combine general education with technical training.",
          source_url: "https://www.dge.mec.pt/cursos-profissionais",
        },
      ],
      no_source: false,
    }),
  });

  render(<DocumentRetrievalScreen bearerToken="token" />);

  fireEvent.change(screen.getByLabelText("Your question"), {
    target: { value: "What are professional courses?" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Search" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(await screen.findByText("Professional Courses Guidance")).toBeInTheDocument();
  expect(
    screen.getByText("Professional courses combine general education with technical training."),
  ).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "https://www.dge.mec.pt/cursos-profissionais" })).toHaveAttribute(
    "href",
    "https://www.dge.mec.pt/cursos-profissionais",
  );
});

test("shows a no-source message when the query is outside the scope of indexed documents", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      documents: [],
      no_source: true,
    }),
  });

  render(<DocumentRetrievalScreen bearerToken="token" />);

  fireEvent.change(screen.getByLabelText("Your question"), {
    target: { value: "What is the weather tomorrow?" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Search" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(await screen.findByRole("status")).toHaveTextContent(
    "No official source is available to answer this query.",
  );
});

test("shows a loading indicator while searching", async () => {
  let resolveFetch: (value: unknown) => void = () => {};
  fetchMock.mockReturnValue(
    new Promise((resolve) => {
      resolveFetch = resolve;
    }),
  );

  render(<DocumentRetrievalScreen bearerToken="token" />);

  fireEvent.change(screen.getByLabelText("Your question"), {
    target: { value: "query" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Search" }));

  expect(screen.getByText("Searching official documents...")).toBeInTheDocument();

  resolveFetch({ ok: true, json: async () => ({ documents: [], no_source: true }) });

  await waitFor(() =>
    expect(screen.queryByText("Searching official documents...")).not.toBeInTheDocument(),
  );
});

test("shows an error message when the request fails", async () => {
  fetchMock.mockResolvedValue({
    ok: false,
    json: async () => ({ message: "Unable to retrieve documents." }),
  });

  render(<DocumentRetrievalScreen bearerToken="token" />);

  fireEvent.change(screen.getByLabelText("Your question"), {
    target: { value: "query" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Search" }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(await screen.findByRole("alert")).toHaveTextContent("Unable to retrieve documents.");
});

test("prompts sign in when no bearer token is present", () => {
  render(<DocumentRetrievalScreen bearerToken={null} />);

  expect(screen.getByText("Sign in to search official documents.")).toBeInTheDocument();
  expect(fetchMock).not.toHaveBeenCalled();
});
