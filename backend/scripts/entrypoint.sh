#!/bin/bash
set -euo pipefail

SECRETS_DIR="${SECRETS_DIR:-/secrets}"
mkdir -p "$SECRETS_DIR"

ENVIRONMENT="${ENVIRONMENT:-development}"

if [ "$ENVIRONMENT" = "production" ]; then
  if [ ! -f "$SECRETS_DIR/jwt_private.pem" ] || [ ! -f "$SECRETS_DIR/jwt_public.pem" ]; then
    echo "ERROR: JWT keys must be provisioned (Vault or mounted secrets) in production."
    exit 1
  fi
elif [ ! -f "$SECRETS_DIR/jwt_private.pem" ]; then
  echo "Generating RS256 JWT key pair (non-production)..."
  openssl genrsa -out "$SECRETS_DIR/jwt_private.pem" 2048
  openssl rsa -in "$SECRETS_DIR/jwt_private.pem" -pubout -out "$SECRETS_DIR/jwt_public.pem"
  chmod 600 "$SECRETS_DIR/jwt_private.pem"
fi

exec "$@"
