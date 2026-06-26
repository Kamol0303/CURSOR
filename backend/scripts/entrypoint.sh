#!/bin/sh
set -eu

# Windows bind-mount: CRLF in .sh files causes "exit 127" (bad shebang)
for f in ./scripts/*.sh; do
  if [ -f "$f" ]; then
    sed -i 's/\r$//' "$f" 2>/dev/null || true
  fi
done

SECRETS_DIR="${SECRETS_DIR:-/secrets}"
mkdir -p "$SECRETS_DIR"

ENVIRONMENT="${ENVIRONMENT:-development}"
SECRETS_BACKEND="${SECRETS_BACKEND:-file}"

if [ "$SECRETS_BACKEND" = "vault" ]; then
  echo "Bootstrapping JWT keys from Vault (${SECRETS_BACKEND})..."
  python - <<'PY'
import asyncio
from app.core.secrets_provider import bootstrap_secrets

asyncio.run(bootstrap_secrets())
PY
fi

if [ "$ENVIRONMENT" = "production" ]; then
  if [ ! -f "$SECRETS_DIR/jwt_private.pem" ] || [ ! -f "$SECRETS_DIR/jwt_public.pem" ]; then
    echo "ERROR: JWT keys must be provisioned (Vault or mounted secrets) in production."
    exit 1
  fi
elif [ ! -f "$SECRETS_DIR/jwt_private.pem" ] || [ ! -f "$SECRETS_DIR/jwt_public.pem" ]; then
  echo "Generating RS256 JWT key pair (${ENVIRONMENT})..."
  openssl genrsa -out "$SECRETS_DIR/jwt_private.pem" 2048
  openssl rsa -in "$SECRETS_DIR/jwt_private.pem" -pubout -out "$SECRETS_DIR/jwt_public.pem"
  chmod 600 "$SECRETS_DIR/jwt_private.pem"
  chmod 644 "$SECRETS_DIR/jwt_public.pem"
fi

exec "$@"
