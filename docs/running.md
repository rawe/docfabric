# Running DocFabric

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Node.js 18+ (for frontend)

## Install dependencies

```bash
cd backend
uv sync
```

## Start the server

```bash
cd backend
uv run uvicorn docfabric.main:app --host 0.0.0.0 --port 8000
```

The server exposes:

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Readiness probe |
| `/api/...` | REST API (see [api-contracts.md](api-contracts.md)) |
| `POST /mcp/` | MCP server (Streamable HTTP) |

## Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`. The Vite dev server proxies `/api` requests to the backend.

## Configuration

Environment variables (or `.env` file in `backend/`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./docfabric.db` | Database connection string |
| `STORAGE_PATH` | `./storage` | Directory for file storage |

## Using with Claude Code

Add a `.mcp.json` to your project root (see [`docs/mcp-example.json`](mcp-example.json)):

```json
{
  "mcpServers": {
    "docfabric": {
      "type": "url",
      "url": "http://localhost:8000/mcp/"
    }
  }
}
```

Edit the `url` to point to your running DocFabric instance. Claude Code will discover the MCP server automatically.
