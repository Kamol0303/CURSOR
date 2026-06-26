@echo off
REM TMB — staging Docker (HTTPS, .env.staging kerak)
cd /d "%~dp0..\.."

if not exist .env.staging (
  echo .env.staging topilmadi. Avval nusxa oling:
  echo   copy .env.staging.example .env.staging
  echo Keyin .env.staging ichidagi CHANGE_ME qiymatlarini to'ldiring.
  exit /b 1
)

if not exist infra\nginx\tls\staging.crt (
  echo TLS sertifikat yo'q. Linux/WSL da:
  echo   ./infra/nginx/generate-dev-certs.sh
  echo yoki staging o'rniga dev ishlating: scripts\windows\update-main.cmd
  exit /b 1
)

docker compose -f docker-compose.staging.yml --env-file .env.staging down
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d --build --remove-orphans

echo.
echo Agar backend unhealthy bo'lsa:
echo   docker compose -f docker-compose.staging.yml --env-file .env.staging logs backend --tail 120
echo.
echo Bazani tozalab qayta (staging ma'lumot o'chadi):
echo   docker compose -f docker-compose.staging.yml --env-file .env.staging down -v
echo   docker compose -f docker-compose.staging.yml --env-file .env.staging up -d --build
