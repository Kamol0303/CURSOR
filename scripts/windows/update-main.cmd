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

git pull --ff-only origin main
if errorlevel 1 (
  echo.
  echo Ogohlantirish: local main origin/main bilan mos kelmaydi.
  echo Local o'zgarishlar o'chiriladi — origin/main ga reset qilinmoqda...
  git reset --hard origin/main
  if errorlevel 1 (
    echo git reset xato — qo'lda: git fetch origin ^&^& git reset --hard origin/main
    exit /b 1
  )
)

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
  echo   scripts\windows\backend-logs.cmd
  echo.
  echo Agar dev bazani tozalash mumkin bo'lsa:
  echo   docker compose down -v
  echo   docker compose up -d --build
  echo   docker compose exec -T backend alembic upgrade head
  echo   docker compose exec -T backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
  exit /b 1
)

echo === 7. Seed — demo loginlar va parollar ===
docker compose exec -T backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
if errorlevel 1 (
  echo.
  echo Seed xato — log: docker compose logs backend --tail 80
  echo Quyidagi statik loginlar baribir ishlashi mumkin:
  call "%~dp0show-credentials.cmd"
  exit /b 1
)

echo.
call "%~dp0show-credentials.cmd"
echo Tayyor!
