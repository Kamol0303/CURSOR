#!/usr/bin/env bash
# TMB — to'liq ishga tushirish (dev yoki staging)
# Ishlatish:
#   ./scripts/start.sh dev       # localhost:3000 + :8000 (eng oson)
#   ./scripts/start.sh staging   # https://tamor.staging.local (nginx + TLS)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MODE="${1:-dev}"

red() { echo -e "\033[31m$*\033[0m"; }
green() { echo -e "\033[32m$*\033[0m"; }
yellow() { echo -e "\033[33m$*\033[0m"; }

require_docker() {
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    return 0
  fi
  red "XATO: Docker topilmadi yoki ishlamayapti."
  echo ""
  echo "Windows + WSL:"
  echo "  1. Docker Desktop ni oching (Running bo'lishi kerak)"
  echo "  2. Settings → Resources → WSL Integration → Ubuntu yoqing"
  echo "  3. WSL terminalni yoping va qayta oching"
  echo "  4. Yoki PowerShell dan: .\\scripts\\start.ps1 $MODE"
  echo ""
  echo "Tekshirish: docker --version && docker compose version"
  exit 1
}

wait_backend() {
  local compose_cmd=("$@")
  yellow "Backend tayyor bo'lishini kutmoqda..."
  for i in $(seq 1 60); do
    if "${compose_cmd[@]}" exec -T backend python -c \
      "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" 2>/dev/null; then
      green "Backend tayyor."
      return 0
    fi
    sleep 2
  done
  red "Backend 2 daqiqada tayyor bo'lmadi. Log: ${compose_cmd[*]} logs backend"
  exit 1
}

seed_users() {
  local compose_cmd=("$@")
  yellow "Demo foydalanuvchilar yuklanmoqda..."
  "${compose_cmd[@]}" exec -T backend python scripts/seed_demo_users.py \
    --i-understand-this-creates-demo-credentials
  green "Seed tugadi."
}

case "$MODE" in
  dev)
    require_docker
    yellow "=== TMB DEV rejimi ==="
    docker compose up -d --build
    wait_backend docker compose
    seed_users docker compose
    echo ""
    green "Tayyor!"
    echo "  Frontend:  http://localhost:3000"
    echo "  Backend:   http://localhost:8000"
    echo "  API docs:  http://localhost:8000/docs"
    echo ""
    yellow "MUHIM: Brauzerda faqat http://localhost:3000 oching!"
    yellow "Cursor/Cloud preview URL (agent.cvm.dev) ishlamaydi — u mahalliy Docker ga ulanmaydi."
    echo ""
    echo "Login (MFA yo'q):"
    echo "  admin.aspect / CenterAdmin#26!"
    ;;

  staging)
    require_docker
    yellow "=== TMB STAGING rejimi ==="

    if [ ! -f .env.staging ]; then
      yellow ".env.staging yaratilmoqda..."
      cp .env.staging.example .env.staging
      # Dev/staging uchun xavfsiz tasodifiy parollar
      DB_PASS="TmbStaging$(openssl rand -hex 4)!"
      sed -i "s/CHANGE_ME_staging_db_password/${DB_PASS}/g" .env.staging
      sed -i "s/CHANGE_ME_32_CHARS_MINIMUM_______/dev-staging-secret-32chars-min!!/g" .env.staging
      green ".env.staging yaratildi."
    fi

    if [ ! -f infra/nginx/tls/fullchain.pem ]; then
      yellow "TLS sertifikatlar yaratilmoqda..."
      bash infra/nginx/generate-dev-certs.sh
    fi

    COMPOSE=(docker compose -f docker-compose.staging.yml --env-file .env.staging)
    "${COMPOSE[@]}" up -d --build
    wait_backend "${COMPOSE[@]}"
    seed_users "${COMPOSE[@]}"

    HOST=$(grep -E '^PUBLIC_HOST=' .env.staging | cut -d= -f2 || echo tamor.staging.local)
    echo ""
    green "Tayyor!"
    echo "  Sayt:      https://${HOST}"
    echo "  API docs:  https://${HOST}/docs (DEBUG yoqilgan bo'lsa)"
    echo ""
    yellow "hosts fayliga qo'shing (bir marta, Admin PowerShell):"
    echo "  Add-Content -Path C:\\Windows\\System32\\drivers\\etc\\hosts -Value \"127.0.0.1 ${HOST}\""
    echo "  Yoki WSL: echo \"127.0.0.1 ${HOST}\" | sudo tee -a /etc/hosts"
    echo ""
    echo "Login (MFA yo'q):"
    echo "  admin.aspect / CenterAdmin#26!"
    echo "Login (MFA bilan):"
    echo "  admin.tmb / Tmb#2026Admin!"
    echo "  MFA QR: ./scripts/show-mfa-qr.sh"
    ;;

  *)
    echo "Ishlatish: $0 dev|staging"
    exit 1
    ;;
esac
