#!/usr/bin/env bash
# Generate self-signed TLS certs for staging only. Use CA-signed certs in production.
set -euo pipefail
DIR="$(cd "$(dirname "$0")/tls" && pwd)"
mkdir -p "$DIR"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$DIR/privkey.pem" \
  -out "$DIR/fullchain.pem" \
  -subj "/CN=tamor.staging.local/O=TMB/C=UZ" \
  -addext "subjectAltName=DNS:tamor.staging.local,DNS:localhost,IP:127.0.0.1" 2>/dev/null \
  || openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$DIR/privkey.pem" \
    -out "$DIR/fullchain.pem" \
    -subj "/CN=tamor.staging.local/O=TMB/C=UZ"
echo "Generated $DIR/fullchain.pem and $DIR/privkey.pem"
echo "NOTE: Browser will warn on self-signed certs. Prefer: ./infra/nginx/generate-mkcert.sh"
