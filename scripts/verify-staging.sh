#!/usr/bin/env bash
# Verify staging HTTPS stack
set -euo pipefail

COMPOSE="docker compose -f docker-compose.staging.yml --env-file .env.staging"
HOST="${PUBLIC_HOST:-tamor.staging.local}"

if [ ! -f infra/nginx/tls/fullchain.pem ]; then
  echo "ERROR: Missing infra/nginx/tls/fullchain.pem — run ./infra/nginx/generate-mkcert.sh" >&2
  exit 1
fi

echo "=== Container status ==="
$COMPOSE ps

echo ""
echo "=== Nginx server_name ==="
$COMPOSE exec nginx nginx -T 2>/dev/null | grep -E "server_name|listen " | head -10

echo ""
echo "=== HTTPS health ==="
curl -fsSk "https://${HOST}/health" && echo ""

echo ""
echo "=== HTTPS frontend ==="
curl -fsSk -o /dev/null -w "HTTPS %{http_code}\n" "https://${HOST}/"

echo ""
echo "=== HTTP redirects to HTTPS ==="
curl -sI "http://${HOST}/" | grep -i "^location:"

echo ""
echo "OK — use https://${HOST} in the browser"
