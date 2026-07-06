#!/bin/sh
set -eu

echo "[production] JWT keys..."
SECRETS_DIR="${SECRETS_DIR:-/secrets}"
mkdir -p "$SECRETS_DIR"
if [ ! -f "$SECRETS_DIR/jwt_private.pem" ] || [ ! -f "$SECRETS_DIR/jwt_public.pem" ]; then
  echo "ERROR: JWT keys must be provisioned via Vault or mounted secrets in production." >&2
  exit 1
fi

echo "[production] Running migrations..."
i=1
while [ "$i" -le 30 ]; do
  if alembic upgrade head; then
    break
  fi
  echo "[production] Migration attempt $i failed, retrying in 2s..."
  sleep 2
  if [ "$i" -eq 30 ]; then
    echo "[production] ERROR: migrations failed after 30 attempts"
    exit 1
  fi
  i=$((i + 1))
done

WORKERS="${UVICORN_WORKERS:-4}"
echo "[production] Starting API server (${WORKERS} workers)..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "$WORKERS" --proxy-headers --forwarded-allow-ips='*'
