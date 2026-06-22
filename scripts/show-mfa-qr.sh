#!/usr/bin/env bash
# Print MFA QR code in terminal for a user (run from project root)
set -euo pipefail

USER="${1:-admin.tmb}"

docker compose -f docker-compose.staging.yml --env-file .env.staging exec -T backend \
  python scripts/show_mfa_qr.py "$USER"
