#!/usr/bin/env bash
# Bir marta: lokal muhit (Git Bash, Docker siz)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "=== TMB local setup (Docker siz) ==="

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "XATO: $1 topilmadi. O'rnating va PATH ga qo'shing."
    exit 1
  fi
}

need_cmd python
need_cmd pip
need_cmd node
need_cmd npm
need_cmd openssl

PYTHON=python
if ! $PYTHON -c "import sys; exit(0 if sys.version_info >= (3,12) else 1)" 2>/dev/null; then
  if command -v py >/dev/null 2>&1; then
    PYTHON="py -3.12"
  else
    echo "XATO: Python 3.12+ kerak"
    exit 1
  fi
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "OGOHLANTIRISH: psql topilmadi."
  echo "PostgreSQL o'rnating: https://www.postgresql.org/download/windows/"
  echo "Keyin: psql -U postgres -f scripts/local/init-db.sql"
else
  echo "PostgreSQL tekshiruvi..."
  if psql -U postgres -d tamor -c "SELECT 1" >/dev/null 2>&1; then
    echo "DB tamor mavjud."
  else
    echo "DB yaratilmoqda (postgres parol so'ralishi mumkin)..."
    psql -U postgres -f scripts/local/init-db.sql || true
  fi
fi

echo "=== Backend .env ==="
if [ ! -f backend/.env ]; then
  cp backend/.env.local.example backend/.env
  echo "backend/.env yaratildi"
fi

mkdir -p backend/secrets
if [ ! -f backend/secrets/jwt_private.pem ]; then
  openssl genrsa -out backend/secrets/jwt_private.pem 2048
  openssl rsa -in backend/secrets/jwt_private.pem -pubout -out backend/secrets/jwt_public.pem
  echo "JWT kalitlar yaratildi: backend/secrets/"
fi

echo "=== Python venv ==="
if [ ! -d backend/.venv ]; then
  $PYTHON -m venv backend/.venv
fi
# shellcheck disable=SC1091
source backend/.venv/Scripts/activate 2>/dev/null || source backend/.venv/bin/activate
pip install -q -r backend/requirements.txt

echo "=== Migration + seed ==="
cd backend
alembic upgrade head
python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
cd "$ROOT"

echo "=== Frontend ==="
if [ ! -f frontend/.env.local ]; then
  cp frontend/.env.local.example frontend/.env.local
fi
cd frontend
npm install
cd "$ROOT"

echo ""
echo "=== Setup tugadi ==="
echo "Ishga tushirish:"
echo "  ./scripts/local/start.sh"
echo ""
echo "Yoki 2 ta Git Bash oyna:"
echo "  ./scripts/local/start-backend.sh"
echo "  ./scripts/local/start-frontend.sh"
