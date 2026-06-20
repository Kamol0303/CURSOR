#!/usr/bin/env bash
# TaMoR backend — quick start (after first-time setup)
set -euo pipefail
cd "$(dirname "$0")"

source .venv/bin/activate
export DATABASE_URL_SYNC="${DATABASE_URL_SYNC:-sqlite:///./tamor.db}"
export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./tamor.db}"
export PYTHONPATH="$(pwd)${PYTHONPATH:+:$PYTHONPATH}"

echo "Backend: http://localhost:8000"
echo "Swagger: http://localhost:8000/docs"
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
