@echo off
REM TMB — main branch yangilanishi va dev Docker qayta ishga tushirish
REM Ishlatish: scripts\windows\update-main.cmd
cd /d "%~dp0..\.."

echo === 1. Git: celerybeat-schedule tozalash (checkout blokini oldini olish) ===
if exist backend\celerybeat-schedule del /f /q backend\celerybeat-schedule

echo === 2. Git: main yangilash ===
git fetch origin
git checkout main
if errorlevel 1 (
  echo checkout xato — celerybeat-schedule yoki boshqa faylni o'chiring va qayta urining
  exit /b 1
)
git pull origin main

echo === 3. Eski staging/dev konteynerlarni to'xtatish ===
docker compose down 2>nul
docker compose -f docker-compose.staging.yml down 2>nul

echo === 4. Dev muhitni qayta build qilish (localhost:3000 / :8000) ===
docker compose up -d --build --remove-orphans
if errorlevel 1 (
  echo Docker xato — log: docker compose logs backend --tail 80
  exit /b 1
)

echo === 5. Backend sog'ligini kutish ===
timeout /t 15 /nobreak >nul

echo === 6. Migratsiya ===
docker compose exec -T backend alembic upgrade head
if errorlevel 1 (
  echo.
  echo Migratsiya xato! Loglarni ko'ring:
  echo   docker compose logs backend --tail 120
  echo.
  echo Agar dev bazani tozalash mumkin bo'lsa:
  echo   docker compose down -v
  echo   docker compose up -d --build
  echo   docker compose exec -T backend alembic upgrade head
  echo   docker compose exec -T backend python scripts/seed_demo_users.py
  exit /b 1
)

echo === 7. Seed (ixtiyoriy — demo loginlar) ===
docker compose exec -T backend python scripts/seed_demo_users.py

echo.
echo ========================================
echo Tayyor!
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   Login:    admin.aspect / CenterAdmin#26!
echo ========================================
