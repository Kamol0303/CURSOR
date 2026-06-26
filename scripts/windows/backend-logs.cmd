@echo off
REM Backend xatosini diagnostika qilish
REM   scripts\windows\backend-logs.cmd          — dev
REM   scripts\windows\backend-logs.cmd staging — staging
cd /d "%~dp0..\.."

set "MODE=dev"
if /I "%~1"=="staging" set "MODE=staging"

if /I "%MODE%"=="staging" (
  set "COMPOSE=docker compose -f docker-compose.staging.yml --env-file .env.staging"
) else (
  set "COMPOSE=docker compose"
)

echo === Konteyner holati (%MODE%) ===
%COMPOSE% ps -a

echo.
echo === Backend oxirgi 120 qator log ===
%COMPOSE% logs backend --tail 120

echo.
echo === Migration holati ===
%COMPOSE% exec -T backend alembic current 2>nul
if errorlevel 1 echo (backend ishlamayapti — yuqoridagi loglarni o'qing)

if /I "%MODE%"=="dev" (
  echo.
  echo === Tez yechim (BAZA O'CHADI — faqat dev) ===
  echo docker compose down -v
  echo docker compose up -d --build --remove-orphans
  echo docker compose exec -T backend alembic upgrade head
  echo docker compose exec -T backend python scripts/seed_demo_users.py
) else (
  echo.
  echo === Tez yechim (BAZA O'CHADI — faqat staging) ===
  echo docker compose -f docker-compose.staging.yml --env-file .env.staging down -v
  echo scripts\windows\staging-up.cmd
)
