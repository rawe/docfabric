# API Contracts

## REST API

Base path: `/api`

### GET /health

Readiness probe.

- **Response:** `200 OK`
  ```json
  { "status": "ok" }
  ```

### POST /api/documents

Upload a new document.

- **Request:** `multipart/form-data`
  - `file` (required) — the document file
  - `metadata` (optional) — JSON string of key-value pairs
- **Response:** `201 Created`
  ```json
  {
    "id": "uuid",
    "filename": "report.pdf",
    "content_type": "application/pdf",
    "size_bytes": 104857,
    "status": "processing",
    "metadata": {},
    "error": null,
    "created_at": "2026-02-28T12:00:00Z",
    "updated_at": "2026-02-28T12:00:00Z"
  }
  ```
- **Behavior:** Stores original file and returns immediately. Markdown conversion runs asynchronously in the background. The `status` field tracks processing progress (see [Document Status Lifecycle](#document-status-lifecycle)). For file types that need no conversion (e.g. `.md`), `status` is `ready` immediately.

### PUT /api/documents/{id}

Replace document file entirely.

- **Request:** `multipart/form-data`
  - `file` (required) — replacement file
- **Response:** `200 OK` — updated document metadata (with `status: "processing"` for converted types)
- **Behavior:** Replaces original file and returns immediately. Markdown re-conversion runs asynchronously. Any in-flight conversion for the previous version is cancelled.

### DELETE /api/documents/{id}

Remove document completely.

- **Response:** `204 No Content`
- **Behavior:** Deletes DB record, original file, and markdown.

### GET /api/documents

List all documents.

- **Query params:**
  - `limit` (int, default 20)
  - `offset` (int, default 0)
- **Response:** `200 OK`
  ```json
  {
    "items": [ ...document metadata objects ],
    "total": 42,
    "limit": 20,
    "offset": 0
  }
  ```
- **Sort:** `created_at DESC` (fixed)

### GET /api/documents/{id}

Get document metadata.

- **Response:** `200 OK` — document metadata object including `status` and `error` fields (no content)

### GET /api/documents/{id}/original

Download original file.

- **Response:** `200 OK` — file stream with original `Content-Type`

### GET /api/documents/{id}/content

Read markdown representation.

- **Query params:**
  - `offset` (int, optional) — character offset
  - `limit` (int, optional) — character count
- **Response:** `200 OK`
  ```json
  {
    "content": "# Document Title\n...",
    "total_length": 15000,
    "offset": 0,
    "length": 15000
  }
  ```
- **Behavior:** Character-based slicing per PRD §6.7.
- **Error:** Returns `409 Conflict` if the document is not yet ready (status is `processing` or `error`):
  ```json
  { "detail": "Document is still processing. Content not available yet.", "status": "processing" }
  ```

### GET /api/documents/{id}/outline

Get document outline (heading structure).

- **Query params:**
  - `mode` (string, optional, default `flat`) — `flat` or `nested`
    - `flat`: each section's `length` covers only its own text, up to the next heading of any level. Sections are non-overlapping; concatenating them reconstructs the full document.
    - `nested`: each section's `length` extends to the next heading at the same or higher level, including all sub-headings. Sections overlap — parent ranges contain their children.
- **Response:** `200 OK`
  ```json
  {
    "sections": [
      { "level": 1, "title": "Introduction", "heading_path": "Introduction", "offset": 0, "length": 32 },
      { "level": 2, "title": "Background",   "heading_path": "Introduction > Background", "offset": 32, "length": 25 }
    ],
    "total_length": 57
  }
  ```
- **Errors:** `404` if document not found, `409` if document is not ready (still processing or failed), `422` if invalid mode.

---

## MCP Server

Mount path: `/mcp`

Read-only access. Four tools:

### Tool: `list_documents`

- **Parameters:**
  - `limit` (int, optional, default 20)
  - `offset` (int, optional, default 0)
- **Returns:** Paginated list with slim items (`id`, `filename` only), plus `total`, `limit`, `offset`

### Tool: `get_document_info`

- **Parameters:**
  - `document_id` (str, required)
- **Returns:** Full document metadata object (JSON), including `status` and `error` fields

### Tool: `get_document_outline`

- **Parameters:**
  - `document_id` (str, required)
  - `mode` (str, optional, default `flat`) — `flat` or `nested`
- **Returns:** Flat list of heading sections with `level`, `title`, `heading_path`, `offset`, `length`, plus `total_length`. The `offset` and `length` values map directly to `read_document_content` parameters, enabling precise section retrieval without reading the entire document.
  - `flat` (default): each section's `length` covers only its own text. Non-overlapping — suitable for sequential document processing.
  - `nested`: each section's `length` includes sub-headings. Parent ranges overlap with children — suitable for retrieving a full section with all its descendants.
- **Rationale:** Lets an LLM navigate large documents structurally — scan headings first, then read only the relevant section.
- If the document is still processing or failed, returns `{"error": "..."}` instead of the outline.

### Tool: `read_document_content`

- **Parameters:**
  - `document_id` (str, required)
  - `offset` (int, optional) — character offset
  - `limit` (int, optional) — character count
- **Returns:** Plain text markdown content. When paginated, includes a compact metadata footer. If the document is still processing or failed, returns a human-readable error message (no exception) directing the LLM to check status via `get_document_info`.

---

## Document Status Lifecycle

Documents have a `status` field that tracks conversion progress:

```
processing  →  ready
processing  →  error
```

| Status | Meaning |
|--------|---------|
| `processing` | File stored, markdown conversion in progress |
| `ready` | Conversion complete, content and outline available |
| `error` | Conversion failed; original file still accessible, but content/outline are not |

When status is `error`, the metadata includes an `error` field with a human-readable reason. File types that need no conversion (e.g. `.md`) skip straight to `ready`.

---

## Error Responses

All endpoints return consistent error format:

```json
{
  "detail": "Document not found"
}
```

| Status | Meaning |
|--------|---------|
| 404 | Document not found |
| 409 | Document not ready (content/outline requested while processing or after error) |
| 422 | Validation error |
| 500 | Internal server error |
