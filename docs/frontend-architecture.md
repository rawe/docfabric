# Frontend Architecture

## Overview

The DocFabric frontend is a single-page application built with React and TypeScript. It communicates with the backend REST API via a Vite dev-server proxy and provides full CRUD operations on documents with markdown preview.

```
┌──────────────────────────────────────────┐
│              Browser (SPA)               │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │          React Router            │    │
│  │  /             → DocumentList    │    │
│  │  /documents/:id → DocumentDetail │    │
│  │  /documents/:id/preview → Preview│    │
│  └──────────┬───────────────────────┘    │
│             │                            │
│  ┌──────────▼───────────────────────┐    │
│  │       TanStack Query             │    │
│  │  Cache, mutations, invalidation  │    │
│  └──────────┬───────────────────────┘    │
│             │                            │
│  ┌──────────▼───────────────────────┐    │
│  │         API Client               │    │
│  │  fetch() → /api/*                │    │
│  └──────────────────────────────────┘    │
└──────────────────────────────────────────┘
         │ Vite proxy (dev)
         ▼
┌──────────────────┐
│  Backend :8000   │
│  FastAPI /api/*  │
└──────────────────┘
```

## Technology Decisions

| Concern | Decision | Rationale |
|---------|----------|-----------|
| Framework | React 19 + TypeScript | Standard, typed, large ecosystem |
| Build tool | Vite | Fast HMR, zero-config TS support |
| Routing | React Router v7 | Declarative, widely adopted |
| Server state | TanStack Query v5 | Caching, mutations, auto-invalidation |
| Markdown | react-markdown + remark-gfm | GFM tables, lightweight |
| Styling | Plain CSS | No build dependencies, sufficient for MVP |

## Pages

### DocumentListPage (`/`)

Paginated table of all documents. Supports upload (modal dialog) and per-row delete (confirmation dialog). Pagination via offset/limit query params to the API.

### DocumentDetailPage (`/documents/:id`)

Displays document metadata (filename, content type, size, timestamps, custom metadata). Actions: download original file, replace file, delete, navigate to content preview.

### DocumentPreviewPage (`/documents/:id/preview`)

Fetches the markdown content and renders it with a raw/rendered toggle. Rendered mode uses `react-markdown` with `remark-gfm` for GFM table support.

## API Client

Thin wrapper around `fetch()` in `src/api/client.ts`. All functions are typed against the backend Pydantic models mirrored in `src/types/document.ts`. The Vite dev server proxies `/api` requests to `http://localhost:8000`.

## State Management

No client-side global state store. All server state is managed by TanStack Query:

- **Queries** cache document lists, individual documents, and content
- **Mutations** handle upload, replace, and delete with automatic cache invalidation
- Query keys: `["documents", offset]`, `["document", id]`, `["content", id]`

## Project Structure

```
frontend/
  src/
    api/
      client.ts          # API client (fetch wrappers)
    types/
      document.ts        # TypeScript interfaces matching backend models
    pages/
      DocumentListPage.tsx
      DocumentDetailPage.tsx
      DocumentPreviewPage.tsx
    components/
      Pagination.tsx     # Offset-based pagination controls
      UploadDialog.tsx   # File upload modal
      ConfirmDialog.tsx  # Delete confirmation modal
    App.tsx              # Router setup
    main.tsx             # Entry point, QueryClient provider
    index.css            # Global styles
  index.html
  vite.config.ts         # Vite config with API proxy
  package.json
```
