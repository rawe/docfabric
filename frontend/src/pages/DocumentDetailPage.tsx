import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { deleteDocument, getDocument, getOriginalUrl, replaceDocument } from "../api/client";
import { ConfirmDialog } from "../components/ConfirmDialog";

export function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const { data: doc, isLoading, error } = useQuery({
    queryKey: ["document", id],
    queryFn: () => getDocument(id!),
    enabled: !!id,
  });

  const replaceMutation = useMutation({
    mutationFn: (file: File) => replaceDocument(id!, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["document", id] });
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteDocument(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      navigate("/");
    },
  });

  function formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString();
  }

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p className="error">Error: {(error as Error).message}</p>;
  if (!doc) return null;

  return (
    <div>
      <Link to="/">&larr; Back to list</Link>

      <div className="page-header">
        <h1>{doc.filename}</h1>
      </div>

      <dl className="metadata">
        <dt>ID</dt>
        <dd><code>{doc.id}</code></dd>
        <dt>Content Type</dt>
        <dd>{doc.content_type}</dd>
        <dt>Size</dt>
        <dd>{formatSize(doc.size_bytes)}</dd>
        <dt>Created</dt>
        <dd>{formatDate(doc.created_at)}</dd>
        <dt>Updated</dt>
        <dd>{formatDate(doc.updated_at)}</dd>
        {Object.keys(doc.metadata).length > 0 && (
          <>
            <dt>Metadata</dt>
            <dd>
              <pre>{JSON.stringify(doc.metadata, null, 2)}</pre>
            </dd>
          </>
        )}
      </dl>

      <div className="actions">
        <Link to={`/documents/${doc.id}/preview`} className="button">
          View Content
        </Link>
        <a href={getOriginalUrl(doc.id)} className="button" download>
          Download Original
        </a>
        <button
          onClick={() => fileRef.current?.click()}
          disabled={replaceMutation.isPending}
        >
          {replaceMutation.isPending ? "Replacing..." : "Replace File"}
        </button>
        <button className="danger" onClick={() => setConfirmDelete(true)}>
          Delete
        </button>
        <input
          ref={fileRef}
          type="file"
          hidden
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) replaceMutation.mutate(file);
          }}
        />
      </div>

      {replaceMutation.isError && (
        <p className="error">{(replaceMutation.error as Error).message}</p>
      )}
      {replaceMutation.isSuccess && <p className="success">File replaced.</p>}

      <ConfirmDialog
        open={confirmDelete}
        title="Delete Document"
        message={`Delete "${doc.filename}"? This cannot be undone.`}
        loading={deleteMutation.isPending}
        onConfirm={() => deleteMutation.mutate()}
        onCancel={() => setConfirmDelete(false)}
      />
    </div>
  );
}
