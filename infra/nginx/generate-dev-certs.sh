#!/usr/bin/env bash
# Generate self-signed TLS certs for staging only. Use CA-signed certs in production.
set -euo pipefail
DIR="$(cd "$(dirname "$0")/tls" && pwd)"
mkdir -p "$DIR"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$DIR/privkey.pem" \
  -out "$DIR/fullchain.pem" \
  -subj "/CN=tamor.local/O=TaMoR/C=UZ"
echo "Generated $DIR/fullchain.pem and $DIR/privkey.pem (staging only)"
