# Implementation Phases

Three phases from zero to Phase 1 MVP.

## Phase A — Foundation ✅

Build the core layers without any HTTP interface.

- Project scaffolding (uv, src layout, dev tooling)
- Configuration (pydantic-settings, .env)
- Database layer (SQLAlchemy Core async, documents table, repository)
- File storage (local disk, originals + markdown)
- Docling converter wrapper (`MarkdownConverter`)
- Document service orchestrating all above (`DocumentNotFoundError` for error signaling)
- Pydantic models (`DocumentMetadata`, `DocumentList`, `DocumentContent`)
- 32 unit tests (models, config, repository, storage, converter, service)

**Outcome:** Full document lifecycle (create, read, list, update, delete) works programmatically. No server needed.

## Phase B — REST API ✅

Expose the document service over HTTP.

- Dependencies added: `fastapi`, `uvicorn[standard]`, `python-multipart`, `httpx` (dev)
- App factory with lifespan context manager (`create_app()`)
- CORS middleware, `DocumentNotFoundError` → 404 exception handler
- Health endpoint at `/health`, all REST endpoints under `/api` per [api-contracts.md](api-contracts.md)
- API router: thin HTTP-to-service wiring, no new business logic
- 20 integration tests via `httpx.AsyncClient` + `ASGITransport` (52 total)

**Outcome:** System is usable via curl/Postman. Full CRUD over HTTP.

## Phase C — MCP Server

Add read-only LLM access.

- FastMCP with 3 tools (list, get, read content)
- Mounted into the FastAPI app at `/mcp`
- Integration tests

**Outcome:** Phase 1 MVP complete. REST + MCP running in one process.

## Phase Dependencies

```
A (Foundation) → B (REST API) → C (MCP Server)
```

Each phase is a commit boundary with passing tests before moving on.
