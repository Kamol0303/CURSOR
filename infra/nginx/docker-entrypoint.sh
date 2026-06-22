#!/usr/bin/env sh
set -eu

rm -f /etc/nginx/conf.d/default.conf

TLS_DIR="/etc/nginx/tls"
FULLCHAIN="${TLS_DIR}/fullchain.pem"
PRIVKEY="${TLS_DIR}/privkey.pem"

if [ ! -f "${FULLCHAIN}" ] || [ ! -f "${PRIVKEY}" ]; then
  echo "ERROR: TLS certificates missing in ${TLS_DIR}" >&2
  echo "Run on the host (before docker compose up):" >&2
  echo "  ./infra/nginx/generate-mkcert.sh" >&2
  echo "Or fallback (browser will warn):" >&2
  echo "  ./infra/nginx/generate-dev-certs.sh" >&2
  exit 1
fi

nginx -t
