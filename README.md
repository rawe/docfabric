# DocFabric

Document infrastructure layer for AI-optimized access.

Upload any document — PDF, DOCX, HTML, or other formats — and DocFabric converts it into a persistent Markdown representation. The original file is stored alongside the generated Markdown, both accessible through a REST API for management and a read-only MCP server for direct LLM consumption.

The core idea: AI systems shouldn't deal with heterogeneous file formats. DocFabric normalizes everything into clean, character-addressable text that agents can navigate structurally (via heading outlines) or read in precise slices (via offset/limit).

## Architecture

DocFabric runs as a single Python process exposing two interfaces:

- **REST API** (`/api`) — Full CRUD for document management (upload, update, delete, list, read)
- **MCP Server** (`/mcp`) — Read-only tools optimized for LLM access (list, info, outline, read)
- **Frontend** (`localhost:5173`) — React SPA for document management via the REST API

Conversion from source formats to Markdown is handled by [docling](https://github.com/DS4SD/docling). Storage uses SQLite + local filesystem. The MCP server uses Streamable HTTP via FastMCP.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `list_documents` | Scan available documents (id + filename) |
| `get_document_info` | Full metadata for a single document |
| `get_document_outline` | Heading structure with offset/length for targeted reads |
| `read_document_content` | Read markdown content (full or partial via offset/limit) |

## Status

### Implemented (Phase 1)

- Document upload with automatic Markdown conversion
- Full REST CRUD (create, read, update, delete, list with pagination)
- Original file download
- Character-based partial reading
- MCP server with 4 read-only tools
- Structural document navigation via heading outlines
- React frontend for document management

### Not yet implemented

- Authentication and authorization
- Semantic search and embeddings
- External source adapters (SharePoint, etc.)
- Document versioning
- Metadata search and filtering
- Multi-tenancy

## Getting Started

### Pre-built images (recommended)

Run DocFabric with Docker using the pre-built images from GitHub Container Registry:

```bash
curl -O https://raw.githubusercontent.com/rawe/docfabric/main/examples/docker-compose/docker-compose.yml
docker compose up -d
```

To pin a specific version instead of `latest`:

```bash
VERSION=0.1.0 docker compose up -d
```

### Docker from source

Build and run from a cloned repository:

```bash
cd docker
docker compose up -d --build
```

### Development mode

Requires [uv](https://docs.astral.sh/uv/) and Node.js:

```bash
cd backend && uv sync      # install Python dependencies
cd ../frontend && npm ci    # install Node dependencies
cd ..
./dev.sh                    # starts backend + frontend with hot-reload
```

### Services

All three options expose the same endpoints:

| Service | Pre-built / Docker | Development |
|---------|--------------------|-------------|
| **UI** | http://localhost:3000 | http://localhost:5173 |
| **REST API** | http://localhost:8000/api | http://localhost:8000/api |
| **MCP Server** | http://localhost:8000/mcp | http://localhost:8000/mcp |

See [docs/releasing.md](docs/releasing.md) for Makefile targets, CI workflow, and configuration reference.

## Claude Code Plugin

DocFabric ships a Claude Code plugin for document upload — the MCP server is read-only, so uploading requires the REST API. Install it from this repository's marketplace:

```bash
claude plugin install docfabric@docfabric-marketplace
```

This adds the `/docfabric:docfabric` skill, which lets Claude upload local files on your behalf.

## Documentation

See [docs/index.md](docs/index.md) for the full documentation index, including PRD, architecture, API contracts, and setup instructions.
