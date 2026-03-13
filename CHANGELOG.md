# Changelog

## 0.2.2

- Fix PDF upload failure in Docker caused by missing `libxcb.so.1` system library. Replaced transitive `opencv-python` dependency with `opencv-python-headless` via uv overrides in `pyproject.toml`. No Dockerfile or docling version changes required.

## 0.2.1

- Add structured error handling for document conversion failures. Conversion errors now return HTTP 422 with a descriptive JSON message instead of a bare 500 Internal Server Error.

## 0.2.0

- Initial release.
