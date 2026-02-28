# Architecture — Phase 1

## System Overview

DocFabric runs as a **single Python process** exposing two interfaces:

1. **REST API** (FastAPI) — Full CRUD for document management
2. **MCP Server** (FastMCP) — Read-only LLM-compatible access, mounted inside the same FastAPI app

```
┌─────────────────────────────────────┐
│           FastAPI Process           │
│                                     │
│  ┌─────────────┐  ┌──────────────┐  │
│  │  REST API   │  │  MCP Server  │  │
│  │  /api/v1/*  │  │  /mcp        │  │
│  └──────┬──────┘  └──────┬───────┘  │
│         │                │          │
│         ▼                ▼          │
│  ┌─────────────────────────────┐    │
│  │      Document Service       │    │
│  └──────┬──────────────┬───────┘    │
│         │              │            │
│         ▼              ▼            │
│  ┌────────────┐ ┌──────────────┐    │
│  │ Repository │ │ File Storage │    │
│  │ (SQLAlchemy│ │ (Local Disk) │    │
│  │  Core)     │ │              │    │
│  └─────┬──────┘ └──────┬───────┘    │
│        │               │            │
│        ▼               ▼            │
│    SQLite DB      ./storage/        │
└─────────────────────────────────────┘
```

## Technology Decisions

| Concern | Decision | Rationale |
|---------|----------|-----------|
| Language | Python 3.12+ | Project requirement |
| Package manager | uv | Project requirement |
| Web framework | FastAPI | Async, Pydantic integration, mature |
| MCP framework | FastMCP | Mounts into FastAPI, decorator-based tools |
| MCP transport | Streamable HTTP | Default FastMCP transport |
| Markdown conversion | docling | Multi-format support (PDF, DOCX, PPTX, HTML, etc.) |
| Database | SQLite (Phase 1) | Zero-config, file-based, sufficient for MVP |
| DB access | SQLAlchemy Core (async) + aiosqlite | Dialect abstraction enables future DB swap without rewriting queries |
| File storage | Local filesystem | Simple, sufficient for Phase 1 |
| ID generation | UUID v4 | No coordination needed, globally unique |

## Component Responsibilities

### REST API Layer
Handles HTTP requests, input validation (Pydantic), file uploads. Delegates to Document Service. See [api-contracts.md](api-contracts.md).

### MCP Server
Read-only tools for LLM access: list, get metadata, read content. Mounted at `/mcp` inside FastAPI via `app.mount()`. See [api-contracts.md](api-contracts.md).

### Document Service
Core business logic. Orchestrates:
- File persistence (save/delete originals)
- Markdown generation (via docling)
- Database operations (via repository)

### Document Repository
Data access via SQLAlchemy Core async engine. Abstracts all SQL. Swappable by changing the connection string (e.g., `sqlite+aiosqlite:///` → `postgresql+asyncpg://`).

### File Storage
Stores originals and markdown representations on local disk. Directory structure:
```
storage/
  originals/{document_id}/{filename}
  markdown/{document_id}.md
```

## Project Structure

```
src/docfabric/
    main.py              # App factory, lifespan, mount MCP
    config.py            # Settings (DB URL, storage path)
    api/
        router.py        # REST endpoints
    mcp/
        server.py        # FastMCP tools
    service/
        document.py      # Business logic
    db/
        engine.py        # AsyncEngine factory
        tables.py        # Table definitions
        repository.py    # DocumentRepository
    conversion/
        converter.py     # docling wrapper
    models/
        document.py      # Pydantic models (API schemas)
tests/
    ...
```

## Data Model

Single table `documents`:

| Column | Type | Notes |
|--------|------|-------|
| id | TEXT PK | UUID v4 |
| filename | TEXT | Original filename |
| content_type | TEXT | MIME type |
| size_bytes | INTEGER | Original file size |
| metadata | JSON | Free-form key-value |
| created_at | TIMESTAMP | UTC, set on create |
| updated_at | TIMESTAMP | UTC, set on create/update |

Files (originals + markdown) are stored on disk, referenced by `id`.

## Database Abstraction Strategy

SQLAlchemy Core provides the abstraction layer:
- Queries use SQLAlchemy expression language (not raw SQL)
- Dialect layer handles SQLite ↔ PostgreSQL differences (parameter binding, JSON, types)
- Swapping DB = changing the connection string + adding the async driver package
- No ABC/Protocol wrapper — YAGNI until a second implementation exists
- Alembic available for future schema migrations
