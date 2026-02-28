# DocFabric

Document infrastructure layer for AI-optimized access.

## Structure

- Monorepo: `backend/` (Python API), `frontend/` (React, planned), `docs/`
- Backend working directory is `backend/` — run `uv` commands from there.

## Technology

- Python uses uv as the package manager. Never use pip.

## Testing

- Run tests from `backend/`: `uv run pytest`
- Tests use in-memory SQLite and `tmp_path` — no external services needed.

## Bugs

- Bug investigation notes go in `.bugs/` (gitignored). Read them for context when picking up a bug.
- Never commit the `.bugs/` folder.

## Rules

- Never add a Co-Authored-By line to commit messages.
