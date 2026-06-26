#!/usr/bin/env bash
# Trusted local HTTPS for staging (mkcert).
# Run on the HOST (WSL/Linux/macOS), not inside the nginx container.
#
# Windows: install mkcert, then run this script from WSL in the project root.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TLS_DIR="${ROOT}/infra/nginx/tls"
DOMAIN="${PUBLIC_HOST:-tamor.staging.local}"

mkdir -p "${TLS_DIR}"

if ! command -v mkcert >/dev/null 2>&1; then
  echo "mkcert not found. Install:"
  echo "  Ubuntu/WSL: sudo apt install libnss3-tools && curl -JLO https://dl.filippo.io/mkcert/latest?for=linux/amd64"
  echo "              chmod +x mkcert-v*-linux-amd64 && sudo mv mkcert-v*-linux-amd64 /usr/local/bin/mkcert"
  echo "  macOS: brew install mkcert"
  exit 1
fi

mkcert -install
mkcert \
  -cert-file "${TLS_DIR}/fullchain.pem" \
  -key-file "${TLS_DIR}/privkey.pem" \
  "${DOMAIN}" localhost 127.0.0.1 ::1

echo ""
echo "Certificates written to ${TLS_DIR}/"
echo "Add to hosts if needed: 127.0.0.1 ${DOMAIN}"
echo "Then: docker compose -f docker-compose.staging.yml --env-file .env.staging up -d --build"
echo "Open: https://${DOMAIN}"
