#!/usr/bin/env bash
# TaMoR backend local setup (WSL/Linux/macOS)
set -euo pipefail

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3.12}"
if ! command -v "$PYTHON" &>/dev/null; then
  PYTHON=python3
fi

echo "Using: $($PYTHON -V)"

# Virtual environment
if [ ! -d .venv ]; then
  $PYTHON -m venv .venv
fi
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# SQLite local dev defaults
export DATABASE_URL_SYNC="${DATABASE_URL_SYNC:-sqlite:///./tamor.db}"
export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./tamor.db}"
export PYTHONPATH="$(pwd)${PYTHONPATH:+:$PYTHONPATH}"

echo "DATABASE_URL_SYNC=$DATABASE_URL_SYNC"
echo "DATABASE_URL=$DATABASE_URL"

python -m alembic -c alembic.ini upgrade head
python -m scripts.seed_demo_users

echo ""
echo "Setup complete. Start the API with:"
echo "  source .venv/bin/activate"
echo "  export DATABASE_URL_SYNC=sqlite:///./tamor.db"
echo "  export DATABASE_URL=sqlite+aiosqlite:///./tamor.db"
echo "  export PYTHONPATH=\$(pwd)"
echo "  uvicorn app.main:app --reload --port 8000"
