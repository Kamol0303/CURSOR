#!/usr/bin/env bash
# TMB — Linux (Kali/Ubuntu/Debian) dev muhitini tozalab ishga tushirish
# Ishlatish: ./scripts/linux-dev-setup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

red() { echo -e "\033[31m$*\033[0m"; }
green() { echo -e "\033[32m$*\033[0m"; }
yellow() { echo -e "\033[33m$*\033[0m"; }

require_docker() {
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    return 0
  fi
  red "XATO: Docker ishlamayapti. Tekshiring: docker info"
  exit 1
}

stop_foreign_port() {
  local port="$1"
  local cid name ports

  while read -r cid name ports; do
    [ -z "$cid" ] && continue
    if echo "$ports" | grep -qE ":${port}->"; then
      if [[ "$name" != cursor-* ]]; then
        yellow "Port ${port} band — boshqa konteyner to'xtatilmoqda: ${name}"
        docker stop "$cid" 2>/dev/null || true
        docker rm "$cid" 2>/dev/null || true
      fi
    fi
  done < <(docker ps --format '{{.ID}} {{.Names}} {{.Ports}}' 2>/dev/null || true)
}

require_docker

yellow "=== 1) Production stackni to'xtatish (agar ishlayotgan bo'lsa) ==="
if [ -f .env.production ]; then
  docker compose -f docker-compose.prod.yml --env-file .env.production down --remove-orphans 2>/dev/null || true
else
  docker compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true
fi

yellow "=== 2) Dev va staging stacklarni to'xtatish ==="
docker compose down --remove-orphans 2>/dev/null || true
if [ -f .env.staging ]; then
  docker compose -f docker-compose.staging.yml --env-file .env.staging down --remove-orphans 2>/dev/null || true
fi

yellow "=== 3) Port ziddiyatlarini bartaraf etish ==="
if command -v systemctl >/dev/null 2>&1; then
  systemctl stop postgresql 2>/dev/null || true
fi
stop_foreign_port 5432
stop_foreign_port 5433
stop_foreign_port 6379

if command -v ss >/dev/null 2>&1 && ss -tlnp 2>/dev/null | grep -q ':5432 '; then
  yellow "Eslatma: 5432 hali band (boshqa loyiha). TMB dev endi 5433 portidan foydalanadi."
  ss -tlnp 2>/dev/null | grep ':5432 ' || true
fi

yellow "=== 4) .env fayli ==="
if [ ! -f .env ]; then
  cp .env.example .env
  green ".env yaratildi (.env.example dan)."
else
  green ".env mavjud."
fi

yellow "=== 5) Dev stack ishga tushirish ==="
chmod +x scripts/start.sh scripts/restart-fresh.sh
exec "$ROOT/scripts/start.sh" dev
