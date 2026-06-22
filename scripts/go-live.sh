#!/usr/bin/env bash
# Production go-live orchestration — run from project root on the prod host
set -euo pipefail

COMPOSE="docker compose -f docker-compose.prod.yml --env-file .env.production"

if [ ! -f .env.production ]; then
  echo "ERROR: Copy and fill .env.production first (see .env.production.example)" >&2
  exit 1
fi

echo "=== 1) Build and start stack ==="
$COMPOSE up -d --build

echo ""
echo "=== 2) Wait for backend healthy ==="
for _ in $(seq 1 60); do
  if $COMPOSE exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)" 2>/dev/null; then
    break
  fi
  sleep 2
done

echo ""
if [ "${GO_LIVE_PURGE:-}" = "yes" ]; then
  echo "=== 3) Purge demo data (GO_LIVE_PURGE=yes) ==="
  $COMPOSE exec -T backend python scripts/purge_demo_data.py \
    --i-understand-this-deletes-demo-data
else
  echo "=== 3) Purge demo data (dry-run) ==="
  $COMPOSE exec -T backend python scripts/purge_demo_data.py \
    --i-understand-this-deletes-demo-data --dry-run
  echo ""
  read -r -p "Execute demo purge? [y/N] " CONFIRM
  if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
    $COMPOSE exec -T backend python scripts/purge_demo_data.py \
      --i-understand-this-deletes-demo-data
  else
    echo "Skipped purge — pre-deploy check may fail if demo data remains."
  fi
fi

echo ""
echo "=== 4) Pre-deploy gate ==="
$COMPOSE exec -T backend python scripts/pre_deploy_check.py

echo ""
echo "=== 5) Post-deploy verification ==="
chmod +x scripts/verify-prod.sh
PUBLIC_HOST="${PUBLIC_HOST:-tamor.toyloq.uz}" ./scripts/verify-prod.sh

echo ""
echo "Go-live steps complete. Complete manual sign-off in docs/red-team-checklist.md"
