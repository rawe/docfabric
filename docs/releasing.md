# Releasing

DocFabric publishes two container images to the GitHub Container Registry (GHCR):

| Image | Description |
|-------|-------------|
| `ghcr.io/rawe/docfabric-server` | FastAPI backend |
| `ghcr.io/rawe/docfabric-ui` | React frontend served via nginx |

## Creating a Release

Tag the commit and push:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The `release-images` GitHub Actions workflow triggers on any `v*` tag push. It builds both images and pushes them to GHCR with the version tag and `latest`.

Alternatively, trigger the workflow manually from the Actions tab with a version string (without the `v` prefix).

## Running with Docker Compose

### Local build

Build and run from source:

```bash
cd docker
docker compose up -d --build
```

- UI: http://localhost:3000
- API: http://localhost:8000
- MCP: http://localhost:8000/mcp

Tear down:

```bash
cd docker
docker compose down
```

### Pre-built images

Use the example compose file to run from GHCR images:

```bash
cd examples/docker-compose
VERSION=1.0.0 docker compose up -d
```

Or use `latest`:

```bash
cd examples/docker-compose
docker compose up -d
```

## Manual Image Build

Build images locally without pushing:

```bash
make release VERSION=1.0.0
```

Build and push:

```bash
make release VERSION=1.0.0 PUSH=true
```

Build a single image:

```bash
make release-server VERSION=1.0.0
make release-ui VERSION=1.0.0
```

## Configuration

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///docfabric.db` | SQLAlchemy database URL |
| `STORAGE_PATH` | `storage` | Directory for uploaded document files |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `API_URL` | `http://docfabric-server:8000` | Backend URL for the nginx `/api` proxy |

## Data Persistence

The docker-compose files mount a `docfabric-data` volume at `/app/data` inside the backend container. This persists the SQLite database and uploaded files across container restarts.
