export interface DocumentMetadata {
  id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  metadata: Record<string, string>;
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
