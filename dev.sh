#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo "Shutting down..."

    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null
        wait "$FRONTEND_PID" 2>/dev/null || true
        echo "  Frontend stopped"
    fi

    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null
        wait "$BACKEND_PID" 2>/dev/null || true
        echo "  Backend stopped"
    fi

    echo "Done."
}

trap cleanup EXIT INT TERM

# --- Backend ---
echo "Starting backend..."
cd "$ROOT_DIR/backend"
uv run uvicorn docfabric.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo -n "Waiting for backend"
until curl -s -o /dev/null http://localhost:8000/health 2>/dev/null; do
    echo -n "."
    sleep 1
done
echo " ready"

# --- Frontend ---
echo "Starting frontend..."
cd "$ROOT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "All services running:"
echo "  Frontend  http://localhost:5173"
echo "  Backend   http://localhost:8000"
echo "  MCP       http://localhost:8000/mcp"
echo ""
echo "Press Ctrl+C to stop all services."

wait
