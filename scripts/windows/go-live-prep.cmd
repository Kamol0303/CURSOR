@echo off
REM TMB — production go-live tayyorgarlik (Windows)
REM Ishlatish: scripts\windows\go-live-prep.cmd
REM Eslatma: haqiqiy production serverda Linux + scripts/go-live.sh ishlatiladi.
cd /d "%~dp0..\.."

echo === TMB Go-Live Tayyorgarlik ===
echo.

echo === 0. Docker tekshiruvi ===
docker info >nul 2>&1
if errorlevel 1 (
  echo XATO: Docker Engine ishlamayapti!
  echo Start menyudan Docker Desktop ni oching va yashil balina kuting.
  start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe" 2>nul
  exit /b 1
)
echo Docker tayyor.
echo.

echo === 1. .env.production mavjudligi ===
if not exist .env.production (
  echo XATO: .env.production topilmadi.
  echo Qo'lda: copy .env.production.example .env.production
  echo Keyin barcha CHANGE_ME qiymatlarni to'ldiring.
  exit /b 1
)
echo .env.production topildi.
echo.

echo === 2. TLS sertifikatlari ===
if not exist infra\nginx\tls\fullchain.pem (
  echo OGOHLANTIRISH: infra\nginx\tls\fullchain.pem yo'q.
  echo Production uchun CA imzolangan sertifikat kerak ^(generate-dev-certs.sh emas^).
) else (
  echo TLS fullchain.pem topildi.
)
if not exist infra\nginx\tls\privkey.pem (
  echo OGOHLANTIRISH: infra\nginx\tls\privkey.pem yo'q.
) else (
  echo TLS privkey.pem topildi.
)
echo.

echo === 3. Production stack build va ishga tushirish ===
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
if errorlevel 1 (
  echo XATO: docker compose prod xato. Log: docker compose -f docker-compose.prod.yml logs backend --tail 80
  exit /b 1
)
echo.

echo === 4. Backend sog'ligini kutish ===
set /a WAIT=0
:wait_backend
docker compose -f docker-compose.prod.yml --env-file .env.production exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)" >nul 2>&1
if not errorlevel 1 goto backend_ok
set /a WAIT+=1
if %WAIT% GEQ 45 (
  echo XATO: Backend 90 soniyada sog'lom bo'lmadi.
  exit /b 1
)
timeout /t 2 /nobreak >nul
goto wait_backend
:backend_ok
echo Backend sog'lom.
echo.

echo === 5. Demo ma'lumot dry-run ===
docker compose -f docker-compose.prod.yml --env-file .env.production exec -T backend python scripts/purge_demo_data.py --i-understand-this-deletes-demo-data --dry-run
if errorlevel 1 (
  echo Ogohlantirish: dry-run xato ^(staging test uchun --allow-non-production qo'shing^).
)
echo.

echo === 6. Pre-deploy gate ===
docker compose -f docker-compose.prod.yml --env-file .env.production exec -T backend python scripts/pre_deploy_check.py
if errorlevel 1 (
  echo XATO: pre_deploy_check o'tmadi. docs/go-live-runbook.md ni ko'ring.
  exit /b 1
)
echo.

echo === Tayyor ===
echo Keyingi qadamlar ^(production serverda^):
echo   1. Demo purge: scripts\purge-demo-data.sh yoki go-live.sh
echo   2. docs/red-team-checklist.md imzolash
echo   3. Vault + CA TLS + UZ hosting tasdiqlash
echo Batafsil: docs\go-live-steps-uz.md
