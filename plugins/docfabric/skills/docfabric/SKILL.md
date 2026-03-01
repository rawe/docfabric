---
name: docfabric
description: "Upload and manage documents in DocFabric. Use when the user wants to ingest files for AI-optimized access."
---

# Goal

Manage documents in DocFabric via its REST API.

## Upload

Upload a local file to DocFabric.

**Script**: `scripts/upload.py`

```bash
uv run scripts/upload.py <file> [--metadata KEY=VALUE ...]
```

**Parameters**:
- `file` (required) — Local file path (PDF, DOCX, PPTX, HTML, CSV, or image)
- `--metadata KEY=VALUE` (optional, repeatable) — Attach metadata key-value pairs

**Output**: `<filename>: <document-id>`

The returned document ID identifies the document for subsequent MCP operations.
