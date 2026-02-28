# DocFabric Frontend

React + TypeScript UI for DocFabric document management.

## Setup

```bash
cd frontend
npm install
npm run dev
```

The dev server starts at `http://localhost:5173` and proxies `/api` requests to the backend at `http://localhost:8000`. Start the backend first.

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server with HMR |
| `npm run build` | Type-check and production build |
| `npm run preview` | Serve production build locally |
| `npm run lint` | Run ESLint |

## Project Structure

```
src/
  api/client.ts              # Typed fetch wrappers for all REST endpoints
  types/document.ts          # TypeScript interfaces (mirrors backend Pydantic models)
  pages/
    DocumentListPage.tsx     # Paginated list, upload, delete
    DocumentDetailPage.tsx   # Metadata, replace, download, delete
    DocumentPreviewPage.tsx  # Markdown raw/rendered toggle (GFM tables)
  components/
    Pagination.tsx           # Offset-based page navigation
    UploadDialog.tsx         # File upload modal
    ConfirmDialog.tsx        # Destructive action confirmation
  App.tsx                    # React Router routes
  main.tsx                   # Entry point, TanStack Query provider
  index.css                  # Global styles
```

## Components

**Pages:**

- **DocumentListPage** — Main landing page. Shows all documents in a table with filename, type, size, and creation date. Upload button opens a modal. Each row has a delete button with confirmation.
- **DocumentDetailPage** — Single document view. Displays all metadata fields. Actions: view content preview, download original file, replace file (re-triggers markdown conversion), delete.
- **DocumentPreviewPage** — Renders the document's markdown content. Toggle between rendered view (with GFM table support) and raw markdown source.

**Shared components:**

- **Pagination** — Previous/Next controls with page indicator. Hidden when total fits in one page.
- **UploadDialog** — Modal with file input. Shows upload progress and errors.
- **ConfirmDialog** — Generic confirmation modal for destructive actions.

## Tech Stack

- **React 19** + **TypeScript** — UI framework
- **Vite** — Build tool and dev server
- **React Router v7** — Client-side routing
- **TanStack Query v5** — Server state, caching, mutations
- **react-markdown** + **remark-gfm** — Markdown rendering with GFM tables
