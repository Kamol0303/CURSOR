#!/bin/bash
set -euo pipefail

echo "[bootstrap] JWT keys..."
SECRETS_DIR="${SECRETS_DIR:-/secrets}"
mkdir -p "$SECRETS_DIR"
if [ ! -f "$SECRETS_DIR/jwt_private.pem" ]; then
  openssl genrsa -out "$SECRETS_DIR/jwt_private.pem" 2048
  openssl rsa -in "$SECRETS_DIR/jwt_private.pem" -pubout -out "$SECRETS_DIR/jwt_public.pem"
  chmod 600 "$SECRETS_DIR/jwt_private.pem"
fi

echo "[bootstrap] Running migrations..."
for i in $(seq 1 30); do
  if alembic upgrade head; then
    break
  fi
  echo "[bootstrap] Migration attempt $i failed, retrying..."
  sleep 2
  if [ "$i" -eq 30 ]; then
    echo "[bootstrap] ERROR: migrations failed"
    exit 1
  fi
done

if [ "${ENVIRONMENT:-development}" = "development" ]; then
  echo "[bootstrap] Seeding demo users (dev only)..."
  python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials || true
fi

echo "[bootstrap] Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
