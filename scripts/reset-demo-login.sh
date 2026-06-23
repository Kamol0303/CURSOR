#!/usr/bin/env bash
# Demo login parollarini qayta tiklash + redis rate-limit tozalash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MODE="${1:-dev}"

if [ "$MODE" = "staging" ]; then
  COMPOSE=(docker compose -f docker-compose.staging.yml --env-file .env.staging)
else
  COMPOSE=(docker compose)
fi

echo "=== Redis rate-limit tozalash ==="
"${COMPOSE[@]}" exec -T redis redis-cli FLUSHDB || true

echo "=== Demo parollar qayta tiklanmoqda ==="
"${COMPOSE[@]}" exec -T backend python scripts/seed_demo_users.py \
  --i-understand-this-creates-demo-credentials

echo ""
echo "=== Login testi ==="
if [ "$MODE" = "staging" ]; then
  ./scripts/test-login.sh admin.aspect 'CenterAdmin#26!'
else
  RESP=$(curl -sS -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/auth/login \
    -H 'Content-Type: application/json' \
    -d '{"username":"admin.aspect","password":"CenterAdmin#26!"}')
  BODY=$(echo "$RESP" | head -n -1)
  CODE=$(echo "$RESP" | tail -n 1)
  echo "HTTP $CODE"
  echo "$BODY" | head -c 400
  echo ""
  if echo "$BODY" | grep -q access_token; then
    echo "OK: Login ishlayapti!"
  else
    echo "XATO: Login ishlamadi — docker compose logs backend --tail 30"
    exit 1
  fi
fi

echo ""
echo "Kiring: http://localhost:3000"
echo "  admin.aspect / CenterAdmin#26!"
