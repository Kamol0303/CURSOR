#!/bin/sh
set -eu

# Ensure default site from the stock image never wins over TaMoR config.
rm -f /etc/nginx/conf.d/default.conf

TLS_DIR="/etc/nginx/tls"
if [ ! -f "${TLS_DIR}/fullchain.pem" ] || [ ! -f "${TLS_DIR}/privkey.pem" ]; then
  mkdir -p "${TLS_DIR}"
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "${TLS_DIR}/privkey.pem" \
    -out "${TLS_DIR}/fullchain.pem" \
    -subj "/CN=tamor.staging.local/O=TaMoR/C=UZ" \
    -addext "subjectAltName=DNS:tamor.staging.local,DNS:localhost,IP:127.0.0.1" 2>/dev/null \
    || openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout "${TLS_DIR}/privkey.pem" \
      -out "${TLS_DIR}/fullchain.pem" \
      -subj "/CN=tamor.staging.local/O=TaMoR/C=UZ"
  echo "TaMoR nginx: generated self-signed TLS certs in ${TLS_DIR}"
fi

nginx -t
