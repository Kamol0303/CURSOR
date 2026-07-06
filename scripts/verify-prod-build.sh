#!/usr/bin/env bash
# Verify production Docker images build without deploying the full stack.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_URL="${NEXT_PUBLIC_API_URL:-https://tamor.toyloq.uz}"

echo "=== 1) Next.js standalone build (host) ==="
(
  cd frontend
  npm ci
  NEXT_PUBLIC_API_URL="$API_URL" npm run build
  test -f .next/standalone/server.js
  test -d .next/static
)
echo "OK: standalone/server.js present"

echo ""
echo "=== 2) Docker: frontend Dockerfile.prod ==="
docker build \
  -f frontend/Dockerfile.prod \
  --build-arg "NEXT_PUBLIC_API_URL=${API_URL}" \
  -t tamor-frontend-prod-verify:local \
  frontend
echo "OK: tamor-frontend-prod-verify:local"

echo ""
echo "=== 3) Docker: backend production image ==="
docker build \
  --build-arg HTTP_PROXY= \
  --build-arg HTTPS_PROXY= \
  --build-arg http_proxy= \
  --build-arg https_proxy= \
  -t tamor-backend-prod-verify:local \
  backend
echo "OK: tamor-backend-prod-verify:local"

echo ""
echo "=== 4) Smoke: standalone container responds ==="
CID="$(docker run -d -p 127.0.0.1:3457:3000 -e HOSTNAME=0.0.0.0 tamor-frontend-prod-verify:local)"
trap 'docker rm -f "$CID" >/dev/null 2>&1 || true' EXIT

for _ in $(seq 1 30); do
  if curl -fsS -o /dev/null "http://127.0.0.1:3457/"; then
    echo "OK: frontend container HTTP 200"
    break
  fi
  sleep 1
done

curl -fsS -o /dev/null "http://127.0.0.1:3457/" || {
  echo "ERROR: frontend container did not respond on :3457" >&2
  docker logs "$CID" --tail 40 >&2 || true
  exit 1
}

echo ""
echo "Production build verification passed."
