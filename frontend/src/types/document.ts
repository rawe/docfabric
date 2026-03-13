export type DocumentStatus = "processing" | "ready" | "error";

export interface DocumentMetadata {
  id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  status: DocumentStatus;
  metadata: Record<string, string>;
  error: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentList {
  items: DocumentMetadata[];
  total: number;
  limit: number;
  offset: number;
}

export interface DocumentContent {
  content: string;
  total_length: number;
  offset: number;
  length: number;
}
