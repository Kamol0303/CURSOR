#!/usr/bin/env bash
# TaMoR frontend — quick start
set -euo pipefail
cd "$(dirname "$0")"

export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000/api/v1}"

echo "Frontend: http://localhost:3000/uz/login"
exec npm run dev
