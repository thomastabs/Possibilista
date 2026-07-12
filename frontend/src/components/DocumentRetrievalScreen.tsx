import React, { useState } from "react";

type DocumentRetrievalResult = {
  title: string;
  content: string;
  source_url: string;
};

type DocumentRetrievalResponse = {
  documents?: DocumentRetrievalResult[];
  no_source?: boolean;
  message?: string;
};

type DocumentRetrievalScreenProps = {
  bearerToken?: string | null;
};

const NO_SOURCE_MESSAGE = "No official source is available to answer this query.";

export function DocumentRetrievalScreen({ bearerToken }: DocumentRetrievalScreenProps) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentRetrievalResult[]>([]);
  const [noSource, setNoSource] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const canSubmit = Boolean(bearerToken && query.trim() && !loading);

  const submitQuery = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!bearerToken) {
      setError("You must be signed in to retrieve documents.");
      return;
    }

    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      setError("Enter a query before submitting.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/v1/documents/retrieve?query=${encodeURIComponent(trimmedQuery)}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${bearerToken}`,
          },
        },
      );

      const data: DocumentRetrievalResponse = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.message || "Unable to retrieve documents.");
      }

      setDocuments(data.documents || []);
      setNoSource(Boolean(data.no_source) || (data.documents || []).length === 0);
      setHasSearched(true);
    } catch (submitError) {
      const message =
        submitError instanceof Error ? submitError.message : "Unable to retrieve documents.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section aria-labelledby="document-retrieval-title" className="document-retrieval-screen">
      <header>
        <h1 id="document-retrieval-title">Official document search</h1>
        <p>Search for official documents supporting an answer.</p>
      </header>

      <form onSubmit={submitQuery} className="document-retrieval-screen__form">
        <label htmlFor="document-retrieval-query">Your question</label>
        <input
          id="document-retrieval-query"
          type="text"
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setError(null);
          }}
          placeholder="Ask about a secondary track, exam, or requirement"
          disabled={loading}
        />
        <button type="submit" disabled={!canSubmit}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      <div aria-live="polite" className="document-retrieval-screen__feedback">
        {loading ? <p>Searching official documents...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
        {!bearerToken ? <p>Sign in to search official documents.</p> : null}
      </div>

      {!loading && !error && hasSearched && noSource ? (
        <p role="status">{NO_SOURCE_MESSAGE}</p>
      ) : null}

      {!loading && !error && !noSource && documents.length > 0 ? (
        <ul className="document-retrieval-screen__results">
          {documents.map((document) => (
            <li key={document.source_url}>
              <h2>{document.title}</h2>
              <p>{document.content}</p>
              <a href={document.source_url} target="_blank" rel="noreferrer">
                {document.source_url}
              </a>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}

export default DocumentRetrievalScreen;
