# Releasing

## Overview

DocFabric publishes two container images to GHCR via a GitHub Actions workflow (`.github/workflows/release-images.yml`). Images are built for both **linux/amd64** and **linux/arm64**.

| Image | Source | Description |
|-------|--------|-------------|
| `ghcr.io/rawe/docfabric-server` | `backend/` | FastAPI backend |
| `ghcr.io/rawe/docfabric-ui` | `frontend/` | React frontend served via nginx |

## Component Versions

Each component tracks its own version independently of the release tag:

| Component | File | Field |
|-----------|------|-------|
| Server | `backend/pyproject.toml` | `version` |
| UI | `frontend/package.json` | `version` |

Component versions do not need to match the git tag, but **must be bumped before tagging** if the component has changed since the last release. The Makefile reads these versions and embeds them as OCI image labels (`COMPONENT_VERSION`).

## Release Steps

1. Bump component versions for any component that changed:

   ```bash
   # backend/pyproject.toml
   version = "0.2.0"

   # frontend/package.json
   "version": "0.2.0"
   ```

2. Commit the version bumps.

3. Tag and push:

   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

The CI workflow triggers on `v*` tag pushes. It builds both images with the tag version and `latest`, then pushes them to GHCR. The workflow can also be triggered manually from the Actions tab with a version string (without the `v` prefix).

## Build Details

The `Makefile` drives all builds. It reads component versions from `backend/pyproject.toml` and `frontend/package.json` and passes them as build args alongside the git commit hash and build date.

| Build arg | Source |
|-----------|--------|
| `VERSION` | Release tag (passed explicitly) |
| `COMPONENT_VERSION` | Component's own version from its manifest |
| `GIT_COMMIT` | `git rev-parse --short HEAD` |
| `BUILD_DATE` | UTC timestamp |

CI builds use registry-based BuildKit cache (`--cache-from`/`--cache-to` with `mode=max`). Local builds skip caching and load directly into the Docker daemon.

```bash
# Local build (host architecture only)
make release VERSION=0.2.0

# CI build (multi-arch, pushes to GHCR)
make release VERSION=0.2.0 PUSH=true

# Single component
make release-server VERSION=0.2.0
make release-ui VERSION=0.2.0
```

## Running with Docker Compose

### From source

```bash
cd docker
docker compose up -d --build
```

### From GHCR images

```bash
cd examples/docker-compose
VERSION=0.2.0 docker compose up -d
```

Or use `latest`:

```bash
cd examples/docker-compose
docker compose up -d
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
