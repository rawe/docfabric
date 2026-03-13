# Changelog

## 0.4.0

- Async document processing: uploads return immediately with a document ID; markdown conversion runs in the background.
- Add `status` field to document metadata (`processing`, `ready`, `error`).
- Content and outline endpoints return 409 while document is still processing.
- Markdown files (`.md`) skip conversion and are ready immediately.
- MCP tools return descriptive messages when content is not yet available.

## 0.3.0

- Add `GET /api/documents/{id}/outline` REST endpoint for document heading structure.
- Support `mode` query parameter (`flat` default, `nested` optional) on both REST and MCP.
- `flat` mode returns non-overlapping sections suitable for text segmentation.
- `nested` mode returns sections where parent ranges include their children.
- Move outline parsing from MCP layer into shared service.

## 0.2.2

- Fix PDF upload failure in Docker caused by missing `libxcb.so.1` system library. Replaced transitive `opencv-python` dependency with `opencv-python-headless` via uv overrides in `pyproject.toml`. No Dockerfile or docling version changes required.

## 0.2.1

- Add structured error handling for document conversion failures. Conversion errors now return HTTP 422 with a descriptive JSON message instead of a bare 500 Internal Server Error.

## 0.2.0

- Initial release.
