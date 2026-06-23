#!/usr/bin/env bash
# Muammo bo'lganda to'liq qayta ishga tushirish (DB volume bilan)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MODE="${1:-dev}"

echo "=== To'xtatish va volume tozalash ==="
if [ "$MODE" = "staging" ]; then
  docker compose -f docker-compose.staging.yml --env-file .env.staging down -v
else
  docker compose down -v
fi

echo "=== Qayta ishga tushirish ==="
exec "$ROOT/scripts/start.sh" "$MODE"
