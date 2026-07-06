@echo off
REM TMB — production image build tekshiruvi (deploy qilmasdan)
REM Ishlatish: scripts\windows\verify-prod-build.cmd
cd /d "%~dp0..\.."

echo === 0. Docker tekshiruvi ===
docker info >nul 2>&1
if errorlevel 1 (
  echo XATO: Docker Engine ishlamayapti!
  start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe" 2>nul
  exit /b 1
)

echo === 1. Next.js build (host) ===
cd frontend
call npm ci
if errorlevel 1 exit /b 1
set NEXT_PUBLIC_API_URL=https://tamor.toyloq.uz
call npm run build
if errorlevel 1 exit /b 1
if not exist .next\standalone\server.js (
  echo XATO: .next\standalone\server.js topilmadi
  exit /b 1
)
cd ..
echo OK: standalone build

echo.
echo === 2. Docker: frontend Dockerfile.prod ===
docker build -f frontend/Dockerfile.prod --build-arg NEXT_PUBLIC_API_URL=https://tamor.toyloq.uz -t tamor-frontend-prod-verify:local frontend
if errorlevel 1 exit /b 1

echo.
echo === 3. Docker: backend image ===
docker build --build-arg HTTP_PROXY= --build-arg HTTPS_PROXY= -t tamor-backend-prod-verify:local backend
if errorlevel 1 exit /b 1

echo.
echo === 4. Frontend konteyner smoke test ===
for /f %%i in ('docker run -d -p 127.0.0.1:3457:3000 -e HOSTNAME=0.0.0.0 tamor-frontend-prod-verify:local') do set CID=%%i
timeout /t 5 /nobreak >nul
curl -fsS -o nul http://127.0.0.1:3457/
if errorlevel 1 (
  echo XATO: frontend konteyner javob bermadi
  docker logs %CID% --tail 40
  docker rm -f %CID% >nul 2>&1
  exit /b 1
)
docker rm -f %CID% >nul 2>&1

echo.
echo Production build tekshiruvi muvaffaqiyatli.
