#!/usr/bin/env bash
# PostgreSQL DB yaratish (Docker siz)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/win-path.sh"
setup_win_paths

if ! command -v psql >/dev/null 2>&1; then
  echo "XATO: psql topilmadi."
  echo ""
  echo "PostgreSQL o'rnating: https://www.postgresql.org/download/windows/"
  echo "Yoki PATH ga qo'shing, masalan:"
  echo '  export PATH="/c/Program Files/PostgreSQL/16/bin:$PATH"'
  echo ""
  echo "Tekshirish: ./scripts/local/check-prereqs.sh"
  exit 1
fi

echo "=== PostgreSQL init ==="
echo "postgres foydalanuvchi paroli so'ralishi mumkin."
echo ""

cd "$ROOT"
psql -U postgres -f scripts/local/init-db.sql

echo ""
echo "DB 'tamor' tayyor. Keyin: ./scripts/local/setup.sh"
