import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ApiError, getDocumentContent } from "../api/client";

export function DocumentPreviewPage() {
  const { id } = useParams<{ id: string }>();
  const [mode, setMode] = useState<"rendered" | "raw">("rendered");

  const { data, isLoading, error } = useQuery({
    queryKey: ["content", id],
    queryFn: () => getDocumentContent(id!),
    enabled: !!id,
    retry: (failureCount, err) => {
      if (err instanceof ApiError && err.status === 409) return failureCount < 60;
      return failureCount < 1;
    },
    retryDelay: 2000,
  });

  const isProcessing = error instanceof ApiError && error.status === 409;

  if (isLoading || isProcessing)
    return <p>{isProcessing ? "Document is still processing..." : "Loading..."}</p>;
  if (error) return <p className="error">Error: {(error as Error).message}</p>;
  if (!data) return null;

  return (
    <div>
      <Link to={`/documents/${id}`}>&larr; Back to document</Link>

      <div className="page-header">
        <h1>Content Preview</h1>
        <div className="toggle">
          <button
            className={mode === "rendered" ? "active" : ""}
            onClick={() => setMode("rendered")}
          >
            Rendered
          </button>
          <button
            className={mode === "raw" ? "active" : ""}
            onClick={() => setMode("raw")}
          >
            Raw
          </button>
        </div>
      </div>

      <p className="meta-line">
        {data.length.toLocaleString()} / {data.total_length.toLocaleString()} characters
      </p>

      {mode === "rendered" ? (
        <div className="markdown-body">
          <Markdown remarkPlugins={[remarkGfm]}>{data.content}</Markdown>
        </div>
      ) : (
        <pre className="raw-content">{data.content}</pre>
      )}
    </div>
  );
}
