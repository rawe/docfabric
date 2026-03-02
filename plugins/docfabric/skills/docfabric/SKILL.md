---
name: docfabric
description: "Manage documents in DocFabric. Use when the user wants to upload, download, or delete documents."
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

## Download

Download a document from DocFabric to a local file.

**Script**: `${CLAUDE_PLUGIN_ROOT}/skills/docfabric/scripts/download.py`

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/docfabric/scripts/download.py <document-id> <output-path> [--markdown]
```

**Parameters**:
- `document-id` (required) — UUID of the document to download
- `output-path` (required) — Local file path to write the document to
- `--markdown` (optional) — Download the markdown representation instead of the original file

**Output**: `<document-id>: saved to <output-path>`

## Delete

Delete a document from DocFabric.

**Script**: `${CLAUDE_PLUGIN_ROOT}/skills/docfabric/scripts/delete.py`

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/docfabric/scripts/delete.py <document-id>
```

**Parameters**:
- `document-id` (required) — UUID of the document to delete

**Output**: `<document-id>: deleted`
