#!/usr/bin/env bash
# Print MFA QR code in terminal for a user (run from project root)
# Usage:
#   ./scripts/show-mfa-qr.sh
#   ./scripts/show-mfa-qr.sh admin.tmb
#   ./scripts/show-mfa-qr.sh --list
set -euo pipefail

COMPOSE="docker compose -f docker-compose.staging.yml --env-file .env.staging"
ARGS=("$@")
if [ ${#ARGS[@]} -eq 0 ]; then
  ARGS=(admin.tmb)
fi

ensure_backend_scripts() {
  if $COMPOSE exec -T backend test -f scripts/show_mfa_qr.py 2>/dev/null; then
    return 0
  fi
  echo "Backend image is outdated (QR scripts missing). Rebuilding backend..."
  $COMPOSE up -d --build backend
  echo "Waiting for backend..."
  for _ in $(seq 1 45); do
    if $COMPOSE exec -T backend test -f scripts/show_mfa_qr.py 2>/dev/null; then
      return 0
    fi
    sleep 2
  done
  echo "ERROR: Backend rebuild did not include show_mfa_qr.py." >&2
  echo "Run: git pull origin CURSOR/fix-postgres-staging-ccd9" >&2
  echo "Then: $COMPOSE up -d --build backend" >&2
  return 1
}

ensure_backend_scripts
$COMPOSE exec -T backend python scripts/show_mfa_qr.py "${ARGS[@]}"
