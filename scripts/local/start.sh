#!/usr/bin/env bash
# Backend + Frontend (Git Bash, Docker siz) — 2 ta fon jarayon
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [ ! -d backend/.venv ]; then
  echo "Avval: ./scripts/local/setup.sh"
  exit 1
fi

cleanup() {
  echo ""
  echo "To'xtatilmoqda..."
  kill "$BACK_PID" "$FRONT_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

bash scripts/local/start-backend.sh &
BACK_PID=$!
sleep 3
bash scripts/local/start-frontend.sh &
FRONT_PID=$!

echo ""
echo "Tayyor! Brauzer: http://localhost:3000"
echo "Login: admin.aspect / CenterAdmin#26!"
echo "To'xtatish: Ctrl+C"
wait
