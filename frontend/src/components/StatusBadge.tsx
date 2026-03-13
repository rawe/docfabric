import type { DocumentStatus } from "../types/document";

const LABELS: Record<DocumentStatus, string> = {
  processing: "Processing",
  ready: "Ready",
  error: "Error",
};

export function StatusBadge({ status }: { status: DocumentStatus }) {
  return <span className={`status-badge status-${status}`}>{LABELS[status]}</span>;
}
