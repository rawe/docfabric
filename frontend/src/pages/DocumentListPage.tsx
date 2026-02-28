import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { deleteDocument, listDocuments, uploadDocument } from "../api/client";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { Pagination } from "../components/Pagination";
import { UploadDialog } from "../components/UploadDialog";

const PAGE_SIZE = 20;

export function DocumentListPage() {
  const queryClient = useQueryClient();
  const [offset, setOffset] = useState(0);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ["documents", offset],
    queryFn: () => listDocuments(PAGE_SIZE, offset),
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadDocument(file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteDocument(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      setDeleteId(null);
    },
  });

  function formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p className="error">Error: {(error as Error).message}</p>;
  if (!data) return null;

  return (
    <div>
      <div className="page-header">
        <h1>Documents</h1>
        <button onClick={() => setUploadOpen(true)}>Upload</button>
      </div>

      {data.items.length === 0 ? (
        <p className="empty">No documents yet. Upload one to get started.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Filename</th>
              <th>Type</th>
              <th>Size</th>
              <th>Created</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((doc) => (
              <tr key={doc.id}>
                <td>
                  <Link to={`/documents/${doc.id}`}>{doc.filename}</Link>
                </td>
                <td>{doc.content_type}</td>
                <td>{formatSize(doc.size_bytes)}</td>
                <td>{formatDate(doc.created_at)}</td>
                <td>
                  <button className="danger small" onClick={() => setDeleteId(doc.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <Pagination
        total={data.total}
        limit={data.limit}
        offset={data.offset}
        onPageChange={setOffset}
      />

      <UploadDialog
        open={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onUpload={async (file) => {
          await uploadMutation.mutateAsync(file);
        }}
      />

      <ConfirmDialog
        open={deleteId !== null}
        title="Delete Document"
        message="Are you sure? This cannot be undone."
        loading={deleteMutation.isPending}
        onConfirm={() => deleteId && deleteMutation.mutate(deleteId)}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
