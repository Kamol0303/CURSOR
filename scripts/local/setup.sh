#!/usr/bin/env bash
# Bir marta: lokal muhit (Git Bash, Docker siz)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/win-path.sh"
setup_win_paths

echo "=== TMB local setup (Docker siz) ==="

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo ""
    echo "XATO: $1 topilmadi."
    echo ""
    echo "Avval tekshiring:"
    echo "  ./scripts/local/check-prereqs.sh"
    echo ""
    echo "O'rnatish qo'llanmasi: docs/windows-install-prereqs.md"
    exit 1
  fi
}

if ! PYTHON="$(resolve_python)"; then
  echo "XATO: Python 3.12+ kerak"
  echo "O'rnatish: https://www.python.org/downloads/ (Add to PATH)"
  exit 1
fi
PIP="$(resolve_pip "$PYTHON")"

need_cmd node
need_cmd npm
need_cmd openssl

if ! command -v psql >/dev/null 2>&1; then
  echo ""
  echo "OGOHLANTIRISH: psql topilmadi — DB avtomatik yaratilmaydi."
  echo "PostgreSQL o'rnating, keyin:"
  echo "  ./scripts/local/init-db.sh"
  echo ""
else
  echo "PostgreSQL tekshiruvi..."
  if psql -U postgres -d tamor -c "SELECT 1" >/dev/null 2>&1; then
    echo "DB tamor mavjud."
  else
    echo "DB yaratilmoqda (postgres parol so'ralishi mumkin)..."
    if psql -U postgres -f scripts/local/init-db.sql; then
      echo "DB tamor yaratildi."
    else
      echo "OGOHLANTIRISH: DB yaratilmadi. Keyinroq: ./scripts/local/init-db.sh"
    fi
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
$PIP install -q -r backend/requirements.txt

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
