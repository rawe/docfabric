# Open Questions — Phase 1

Questions to resolve before implementation.

## Must Decide

1. **Supported file formats** — Which formats does Phase 1 accept for upload? Docling supports PDF, DOCX, PPTX, HTML, CSV, EPUB, images. Do we accept all, or restrict to a subset (e.g., PDF + DOCX only)?

2. **Docling resource footprint** — Docling depends on PyTorch and ML models (~GB-scale install). Is this acceptable for the MVP, or should we start with a lighter alternative and swap later?

3. **Conversion mode** — Docling can run CPU-only or with GPU acceleration. Phase 1 is CPU-only?

4. **Max concurrent conversions** — Document conversion via docling is CPU-intensive. Should we limit concurrency (e.g., process one at a time via a queue), or let FastAPI handle it with async workers?

5. **Configuration approach** — Environment variables only, or a config file (e.g., `.env`)? Suggested: env vars with python-dotenv for local dev.

6. **API versioning** — PRD doesn't mention versioning. Proposed `/api/v1` prefix. Acceptable?

## Nice to Clarify

7. **Health endpoint** — Add a `GET /health` for readiness checks?

8. **CORS** — Enable CORS for browser-based clients, or API-only for now?

9. **Logging** — Structured logging (JSON) from the start, or plain text for MVP?

10. **Testing strategy** — Unit tests with in-memory SQLite + mocked file storage? Integration tests with real filesystem?
