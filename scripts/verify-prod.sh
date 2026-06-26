#!/usr/bin/env bash
# Post-deploy production verification
set -euo pipefail

COMPOSE="docker compose -f docker-compose.prod.yml --env-file .env.production"
HOST="${PUBLIC_HOST:-tamor.toyloq.uz}"

if [ ! -f .env.production ]; then
  echo "ERROR: Missing .env.production — cp .env.production.example .env.production" >&2
  exit 1
fi

if [ ! -f "infra/nginx/tls/fullchain.pem" ]; then
  echo "ERROR: Missing infra/nginx/tls/fullchain.pem — install CA-signed certs before go-live" >&2
  exit 1
fi

echo "=== Container status ==="
$COMPOSE ps

echo ""
echo "=== Pre-deploy gate (in-container) ==="
$COMPOSE exec -T backend python scripts/pre_deploy_check.py

echo ""
echo "=== HTTPS health ==="
curl -fsS "https://${HOST}/health" && echo ""

echo ""
echo "=== Frontend ==="
curl -fsS -o /dev/null -w "HTTPS %{http_code}\n" "https://${HOST}/"

echo ""
echo "=== OpenAPI docs hidden (DEBUG=false) ==="
DOCS_CODE=$(curl -sS -o /dev/null -w "%{http_code}" "https://${HOST}/docs" || true)
if [ "$DOCS_CODE" = "404" ] || [ "$DOCS_CODE" = "403" ]; then
  echo "OK: /docs not exposed (HTTP ${DOCS_CODE})"
else
  echo "WARNING: /docs returned HTTP ${DOCS_CODE} — expected 404 in production"
fi

echo ""
echo "=== Red-team automated checks ==="
python3 scripts/red_team_verify.py --url "https://${HOST}" --production

echo ""
echo "OK — production checks passed for https://${HOST}"
echo "Manual: login with real super_admin + MFA, SMS OTP, backup restore drill (RT-25–28)"
