@echo off
REM TMB — staging Docker (HTTPS, .env.staging kerak)
cd /d "%~dp0..\.."

if not exist .env.staging (
  echo .env.staging topilmadi — avtomatik yaratilmoqda...
  call "%~dp0setup-staging-env.cmd"
  if errorlevel 1 exit /b 1
)

if not exist infra\nginx\tls\fullchain.pem (
  echo TLS sertifikat yo'q ^(fullchain.pem^).
  echo Git Bash yoki WSL da bajaring:
  echo   bash infra/nginx/generate-dev-certs.sh
  echo.
  echo Yoki dev muhit uchun:
  echo   scripts\windows\update-main.cmd
  exit /b 1
)

if not exist infra\nginx\tls\privkey.pem (
  echo TLS privkey.pem yo'q — generate-dev-certs.sh ni qayta ishga tushiring.
  exit /b 1
)

echo === Eski staging konteynerlarni to'xtatish ===
docker compose -f docker-compose.staging.yml --env-file .env.staging down

echo === Staging build va ishga tushirish ===
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d --build --remove-orphans
if errorlevel 1 (
  echo Docker xato — log: scripts\windows\backend-logs.cmd staging
  exit /b 1
)

echo.
echo Backend sog'ligini kutish ^(90 soniyagacha^)...
timeout /t 20 /nobreak >nul
docker compose -f docker-compose.staging.yml --env-file .env.staging exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)" 2>nul
if errorlevel 1 (
  echo.
  echo Backend hali tayyor emas yoki xato. Loglarni ko'ring:
  echo   scripts\windows\backend-logs.cmd staging
  echo.
  echo Ko'pincha yechim — staging bazasini tozalash:
  echo   docker compose -f docker-compose.staging.yml --env-file .env.staging down -v
  echo   scripts\windows\staging-up.cmd
  exit /b 1
)

echo === Demo foydalanuvchilar ===
docker compose -f docker-compose.staging.yml --env-file .env.staging exec -T backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials

echo.
echo ========================================
echo Staging tayyor!
echo   https://tamor.staging.local
echo   hosts: 127.0.0.1 tamor.staging.local
echo   Login: admin.aspect / CenterAdmin#26!
echo ========================================
