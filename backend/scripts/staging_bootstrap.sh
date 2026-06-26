#!/bin/sh
set -eu

echo "[staging] JWT keys..."
SECRETS_DIR="${SECRETS_DIR:-/secrets}"
mkdir -p "$SECRETS_DIR"
if [ ! -f "$SECRETS_DIR/jwt_private.pem" ] || [ ! -f "$SECRETS_DIR/jwt_public.pem" ]; then
  openssl genrsa -out "$SECRETS_DIR/jwt_private.pem" 2048
  openssl rsa -in "$SECRETS_DIR/jwt_private.pem" -pubout -out "$SECRETS_DIR/jwt_public.pem"
  chmod 600 "$SECRETS_DIR/jwt_private.pem"
  chmod 644 "$SECRETS_DIR/jwt_public.pem"
fi

echo "[staging] Running migrations..."
i=1
while [ "$i" -le 30 ]; do
  if alembic upgrade head; then
    break
  fi
  echo "[staging] Migration attempt $i failed, retrying in 2s..."
  sleep 2
  if [ "$i" -eq 30 ]; then
    echo "[staging] ERROR: migrations failed after 30 attempts"
    exit 1
  fi
  i=$((i + 1))
done

echo "[staging] Starting API server (2 workers)..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips='*'
