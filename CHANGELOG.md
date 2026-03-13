# Changelog

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
