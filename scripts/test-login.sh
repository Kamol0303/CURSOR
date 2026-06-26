#!/usr/bin/env bash
# Test login API through nginx (run from project root)
set -euo pipefail

HOST="${PUBLIC_HOST:-tamor.staging.local}"
# Default: no-MFA account for quick smoke test. Override: ./scripts/test-login.sh admin.tmb 'Tmb#2026Admin!'
USER="${1:-admin.aspect}"
PASS="${2:-CenterAdmin#26!}"

echo "=== Health ==="
curl -fsSk "https://${HOST}/health" && echo ""

echo ""
echo "=== Login POST (${USER}) ==="
HTTP_CODE=$(curl -sSk -o /tmp/tmb-login-test.json -w "%{http_code}" -X POST "https://${HOST}/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${USER}\",\"password\":\"${PASS}\"}")
RESP=$(cat /tmp/tmb-login-test.json)
echo "HTTP ${HTTP_CODE}"
echo "$RESP" | head -c 500
echo ""

if echo "$RESP" | grep -q requires_mfa_setup; then
  echo ""
  echo "OK: Login works — MFA setup required (open browser to complete)."
elif echo "$RESP" | grep -q '"requires_mfa":true'; then
  echo ""
  echo "OK: Login works — enter TOTP code in browser."
elif echo "$RESP" | grep -q access_token; then
  echo ""
  echo "OK: Login works — token received."
elif echo "$RESP" | grep -q INVALID_CREDENTIALS || [ "$HTTP_CODE" = "401" ]; then
  echo ""
  echo "FAIL: Wrong username/password OR demo seed not run."
  echo "Run:"
  echo "  docker compose -f docker-compose.staging.yml --env-file .env.staging exec -T backend \\"
  echo "    python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials"
  echo ""
  echo "Then retry: ./scripts/test-login.sh"
  echo "Or with MFA admin: ./scripts/test-login.sh admin.tmb 'Tmb#2026Admin!'"
  exit 1
else
  echo ""
  echo "Unexpected response — check JSON above."
  exit 1
fi
