#!/usr/bin/env bash
# Test login API through nginx (run from project root)
set -euo pipefail

HOST="${PUBLIC_HOST:-tamor.staging.local}"
USER="${1:-admin.tmb}"
PASS="${2:-Tmb#2026Admin!}"

echo "=== Health ==="
curl -fsSk "https://${HOST}/health" && echo ""

echo ""
echo "=== Login POST ==="
RESP=$(curl -fsSk -X POST "https://${HOST}/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${USER}\",\"password\":\"${PASS}\"}")
echo "$RESP" | head -c 500
echo ""

if echo "$RESP" | grep -q requires_mfa_setup; then
  echo ""
  echo "OK: Login works — MFA setup required (open browser to complete)."
elif echo "$RESP" | grep -q access_token; then
  echo ""
  echo "OK: Login works — token received."
elif echo "$RESP" | grep -q INVALID_CREDENTIALS; then
  echo ""
  echo "FAIL: Wrong username/password OR seed not run."
  echo "Run: docker compose -f docker-compose.staging.yml --env-file .env.staging exec -T backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials"
  echo "Try also: admin.tamor / Tamor#2026Admin! (old seed)"
else
  echo ""
  echo "Check response above."
fi
