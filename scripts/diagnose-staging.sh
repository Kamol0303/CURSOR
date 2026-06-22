#!/usr/bin/env bash
# Diagnose staging stack issues (backend restart loop, seed failures)
set -euo pipefail

COMPOSE="docker compose -f docker-compose.staging.yml --env-file .env.staging"

echo "=== Container status ==="
$COMPOSE ps -a

echo ""
echo "=== Backend last 40 log lines ==="
$COMPOSE logs backend --tail 40 2>&1 || true

echo ""
echo "=== Postgres last 10 log lines ==="
$COMPOSE logs postgres --tail 10 2>&1 || true

echo ""
echo "=== Nginx last 10 log lines ==="
$COMPOSE logs nginx --tail 10 2>&1 || true

BACKEND_STATE=$($COMPOSE ps backend --format '{{.State}}' 2>/dev/null || echo "unknown")
if echo "$BACKEND_STATE" | grep -qi restarting; then
  echo ""
  echo "!!! Backend is RESTARTING — common fixes:"
  echo "  1) DB password mismatch — .env.staging POSTGRES_PASSWORD must match the volume."
  echo "     Fix: docker compose -f docker-compose.staging.yml --env-file .env.staging down -v"
  echo "     Then up again (DELETES database data)."
  echo "  2) Missing TLS: ./infra/nginx/generate-mkcert.sh"
  echo "  3) See full logs: $COMPOSE logs backend --tail 200"
fi

if $COMPOSE ps backend --format '{{.State}}' 2>/dev/null | grep -qi running; then
  echo ""
  echo "=== Seed demo users ==="
  $COMPOSE exec -T backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
fi
