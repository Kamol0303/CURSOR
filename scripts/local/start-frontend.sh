#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/win-path.sh"
setup_win_paths
cd "$ROOT/frontend"

if ! command -v npm >/dev/null 2>&1; then
  echo "XATO: npm topilmadi. ./scripts/local/check-prereqs.sh"
  exit 1
fi

if [ -f .env.local ]; then
  set -a
  # shellcheck disable=SC1091
  source .env.local
  set +a
fi

export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"
echo "Frontend: http://localhost:3000"
echo "API: $NEXT_PUBLIC_API_URL"
exec npm run dev -- --hostname 0.0.0.0 --port 3000
