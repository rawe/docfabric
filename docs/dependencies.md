# Dependencies

## Docling

DocFabric uses [docling](https://github.com/DS4SD/docling) for document-to-markdown conversion. Docling brings a deep transitive dependency tree including PyTorch, OpenCV, and several ML model libraries.

### OpenCV headless override

Docling pulls in `opencv-python` transitively (via `rapidocr`). The full `opencv-python` package requires X11/GUI system libraries (`libxcb`, `libgl1`, etc.) that are not present in slim Docker base images and are unnecessary for a headless server.

To avoid bloating the Docker image with unused GUI dependencies, `pyproject.toml` overrides the dependency:

```toml
[tool.uv]
override-dependencies = ["opencv-python-headless>=4"]
constraint-dependencies = ["opencv-python<0"]
```

- `override-dependencies` tells uv to resolve `opencv-python-headless` wherever `opencv-python` is requested.
- `constraint-dependencies` with `<0` prevents the full `opencv-python` from ever being installed.
- `opencv-python-headless` is API-identical to `opencv-python`, just compiled without GUI bindings.

This override is transparent to docling updates — no version pinning is needed.

### OCR engines

Docling supports several OCR engines. As of v0.2.2, no OCR engine is explicitly installed. Docling logs `WARNING: No OCR engine found` at startup. If OCR-based text extraction from scanned PDFs is needed, add one of: `easyocr`, `rapidocr`, `tesserocr`.
