#!/usr/bin/env bash
# Demo login parollarini qayta tiklash (DB ni o'chirmaydi)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MODE="${1:-dev}"

if [ "$MODE" = "staging" ]; then
  COMPOSE=(docker compose -f docker-compose.staging.yml --env-file .env.staging)
else
  COMPOSE=(docker compose)
fi

echo "=== Demo parollar qayta tiklanmoqda ==="
"${COMPOSE[@]}" exec -T backend python scripts/seed_demo_users.py \
  --i-understand-this-creates-demo-credentials

echo ""
echo "=== Login (MFA yo'q — shu bilan kiring) ==="
echo "  admin.aspect"
echo "  CenterAdmin#26!"
echo ""
echo "=== MFA bilan (Google Authenticator kerak) ==="
echo "  admin.tmb / Tmb#2026Admin!"
echo "  QR kod: ./scripts/show-mfa-qr.sh"
echo ""
echo "=== Tekshirish ==="
if [ "$MODE" = "staging" ]; then
  ./scripts/test-login.sh admin.aspect 'CenterAdmin#26!'
else
  curl -sS -X POST http://localhost:8000/api/v1/auth/login \
    -H 'Content-Type: application/json' \
    -d '{"username":"admin.aspect","password":"CenterAdmin#26!"}' | head -c 300
  echo ""
fi
