---
name: docfabric
description: "Manage documents in DocFabric. Use when the user wants to upload or delete documents."
---

# Goal

Manage documents in DocFabric via its REST API.

## Upload

Upload a local file to DocFabric.

**Script**: `${CLAUDE_PLUGIN_ROOT}/skills/docfabric/scripts/upload.py`

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/docfabric/scripts/upload.py <file> [--metadata KEY=VALUE ...]
```

**Parameters**:
- `file` (required) — Local file path (PDF, DOCX, PPTX, HTML, CSV, or image)
- `--metadata KEY=VALUE` (optional, repeatable) — Attach metadata key-value pairs

**Output**: `<filename>: <document-id>`

The returned document ID identifies the document for subsequent MCP operations.

## Delete

Delete a document from DocFabric.

**Script**: `${CLAUDE_PLUGIN_ROOT}/skills/docfabric/scripts/delete.py`

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/docfabric/scripts/delete.py <document-id>
```

**Parameters**:
- `document-id` (required) — UUID of the document to delete

**Output**: `<document-id>: deleted`
