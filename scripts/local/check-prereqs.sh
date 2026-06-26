#!/usr/bin/env bash
# Talab qilinadigan dasturlarni tekshirish (Git Bash, Windows)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/win-path.sh"
setup_win_paths

ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MISSING=0
WARN=0

ok() { echo "  [OK] $1"; }
fail() { echo "  [XATO] $1"; MISSING=1; }
warn() { echo "  [OGOH] $1"; WARN=1; }

echo "=== TMB — talablar tekshiruvi ==="
echo "Papka: $ROOT"
echo ""

echo "Python 3.12+:"
if PYTHON_CMD="$(resolve_python)"; then
  VER="$($PYTHON_CMD --version 2>&1)"
  ok "$PYTHON_CMD — $VER"
else
  fail "Python 3.12+ topilmadi"
  echo "       O'rnatish: https://www.python.org/downloads/"
  echo "       Belgilang: Add python.exe to PATH"
fi

echo ""
echo "pip:"
if [ "${PYTHON_CMD:-}" != "" ]; then
  PIP_CMD="$(resolve_pip "$PYTHON_CMD")"
  if $PIP_CMD --version >/dev/null 2>&1; then
    ok "$PIP_CMD"
  else
    fail "pip ishlamayapti — $PIP_CMD --version"
  fi
else
  fail "pip (Python yo'q)"
fi

echo ""
echo "Node.js:"
if command -v node >/dev/null 2>&1; then
  ok "node $(node --version)"
else
  fail "node topilmadi"
  echo "       O'rnatish: https://nodejs.org/ (LTS, 20+)"
  echo "       O'rnatgach Git Bash ni yoping va qayta oching"
fi

echo ""
echo "npm:"
if command -v npm >/dev/null 2>&1; then
  ok "npm $(npm --version)"
else
  fail "npm topilmadi (Node.js bilan keladi)"
fi

echo ""
echo "PostgreSQL (psql):"
if command -v psql >/dev/null 2>&1; then
  ok "psql $(psql --version | head -1)"
  if psql -U postgres -d tamor -c "SELECT 1" >/dev/null 2>&1; then
    ok "DB 'tamor' ulanishi muvaffaqiyatli"
  elif psql -U postgres -c "SELECT 1" >/dev/null 2>&1; then
    warn "postgres ulanadi, lekin DB 'tamor' yo'q"
    echo "       Yaratish: ./scripts/local/init-db.sh"
  else
    warn "psql bor, lekin postgres ga ulanib bo'lmadi (parol yoki xizmat)"
    echo "       Windows: Services → postgresql xizmati ishga tushiring"
    echo "       Keyin: ./scripts/local/init-db.sh"
  fi
else
  fail "psql topilmadi"
  echo "       O'rnatish: https://www.postgresql.org/download/windows/"
  echo "       O'rnatishda Stack Builder dan keyin PATH ga qo'shing yoki Git Bash ni qayta oching"
  echo "       Qo'lda PATH: C:\\Program Files\\PostgreSQL\\16\\bin"
fi

echo ""
echo "OpenSSL:"
if command -v openssl >/dev/null 2>&1; then
  ok "openssl"
else
  fail "openssl topilmadi (Git for Windows qayta o'rnating)"
fi

echo ""
if [ "$MISSING" -eq 0 ]; then
  echo "=== Hammasi tayyor ==="
  if [ "$WARN" -ne 0 ]; then
    echo "Ba'zi ogohlantirishlar bor — yuqoridagi qadamlarni bajaring."
  else
    echo "Keyingi qadam:"
    echo "  ./scripts/local/setup.sh"
  fi
  exit 0
fi

echo "=== Yetishmayotgan dasturlar bor ==="
echo "Batafsil: docs/windows-install-prereqs.md"
echo ""
echo "O'rnatgach:"
echo "  1. Git Bash oynasini yoping va qayta oching"
echo "  2. ./scripts/local/check-prereqs.sh"
echo "  3. ./scripts/local/init-db.sh   (PostgreSQL uchun)"
echo "  4. ./scripts/local/setup.sh"
exit 1
