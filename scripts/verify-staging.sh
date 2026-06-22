#!/usr/bin/env bash
# Quick staging stack verification after docker compose up
set -euo pipefail

COMPOSE="docker compose -f docker-compose.staging.yml --env-file .env.staging"
HOST="${PUBLIC_HOST:-tamor.staging.local}"

echo "=== Container status ==="
$COMPOSE ps

echo ""
echo "=== Nginx config (first 15 lines) ==="
$COMPOSE exec nginx head -n 15 /etc/nginx/nginx.conf

echo ""
echo "=== Nginx test ==="
$COMPOSE exec nginx nginx -t

echo ""
echo "=== HTTP health ==="
curl -fsS "http://${HOST}/health" && echo ""

echo ""
echo "=== HTTP frontend (status code) ==="
curl -sS -o /dev/null -w "HTTP %{http_code}\n" "http://${HOST}/"

echo ""
echo "=== API login endpoint (expect 422 without body) ==="
curl -sS -o /dev/null -w "HTTP %{http_code}\n" -X POST "http://${HOST}/api/v1/auth/login" \
  -H "Content-Type: application/json" -d '{}'

echo ""
echo "OK — if health returns JSON and frontend is not 502, nginx proxy is working."
