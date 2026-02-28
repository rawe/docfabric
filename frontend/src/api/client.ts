import type { DocumentContent, DocumentList, DocumentMetadata } from "../types/document";

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function listDocuments(limit = 20, offset = 0): Promise<DocumentList> {
  return request(`/documents?limit=${limit}&offset=${offset}`);
}

export async function getDocument(id: string): Promise<DocumentMetadata> {
  return request(`/documents/${id}`);
}

export async function getDocumentContent(
  id: string,
  offset?: number,
  limit?: number,
): Promise<DocumentContent> {
  const params = new URLSearchParams();
  if (offset !== undefined) params.set("offset", String(offset));
  if (limit !== undefined) params.set("limit", String(limit));
  const qs = params.toString();
  return request(`/documents/${id}/content${qs ? `?${qs}` : ""}`);
}

export async function uploadDocument(
  file: File,
  metadata?: Record<string, string>,
): Promise<DocumentMetadata> {
  const form = new FormData();
  form.append("file", file);
  if (metadata) form.append("metadata", JSON.stringify(metadata));

  const res = await fetch(`${BASE}/documents`, { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? `Upload failed: ${res.status}`);
  }
  return res.json();
}

export async function replaceDocument(id: string, file: File): Promise<DocumentMetadata> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${BASE}/documents/${id}`, { method: "PUT", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? `Replace failed: ${res.status}`);
  }
  return res.json();
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${BASE}/documents/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? `Delete failed: ${res.status}`);
  }
}

export function getOriginalUrl(id: string): string {
  return `${BASE}/documents/${id}/original`;
}
