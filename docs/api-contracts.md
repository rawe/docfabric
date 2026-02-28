# API Contracts — Phase 1

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
    "metadata": {},
    "created_at": "2026-02-28T12:00:00Z",
    "updated_at": "2026-02-28T12:00:00Z"
  }
  ```
- **Behavior:** Stores original file, generates markdown via docling, persists both.

### PUT /api/documents/{id}

Replace document file entirely.

- **Request:** `multipart/form-data`
  - `file` (required) — replacement file
- **Response:** `200 OK` — updated document metadata
- **Behavior:** Replaces original file, regenerates markdown, updates `updated_at`.

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

- **Response:** `200 OK` — document metadata object (no content)

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

---

## MCP Server

Mount path: `/mcp`

Read-only access. Three tools:

### Tool: `list_documents`

- **Parameters:**
  - `limit` (int, optional, default 20)
  - `offset` (int, optional, default 0)
- **Returns:** Paginated list with slim items (`id`, `filename` only), plus `total`, `limit`, `offset`

### Tool: `get_document_info`

- **Parameters:**
  - `document_id` (str, required)
- **Returns:** Full document metadata object (JSON)

### Tool: `read_document_content`

- **Parameters:**
  - `document_id` (str, required)
  - `offset` (int, optional) — character offset
  - `limit` (int, optional) — character count
- **Returns:** Plain text markdown content. When paginated, includes a compact metadata footer

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
| 422 | Validation error |
| 500 | Internal server error |
