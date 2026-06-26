@echo off
REM TMB — merge conflict va YAML xatosidan keyin repozitoriyani tiklash
REM Ishlatish: scripts\windows\recover-repo.cmd
cd /d "%~dp0..\.."

echo === 1. Merge bekor qilish (agar bor bo'lsa) ===
git merge --abort 2>nul

echo === 2. Toza branch olish ===
git fetch origin
git checkout CURSOR/tenant-rbac-ccd9 2>nul
if errorlevel 1 (
  echo Branch yo'q — yaratilmoqda...
  git checkout -b CURSOR/tenant-rbac-ccd9 origin/CURSOR/tenant-rbac-ccd9
)
git reset --hard origin/CURSOR/tenant-rbac-ccd9

echo === 3. Conflict marker tekshiruvi ===
findstr /s /m /c:"<<<<<<<" docker-compose.yml backend\app\*.py 2>nul
if not errorlevel 1 (
  echo XATO: Hali conflict markerlar bor! Qo'lda tuzating.
  exit /b 1
)

echo === 4. Docker qayta ishga tushirish ===
docker compose down 2>nul
docker compose build backend
call scripts\start.cmd

echo.
echo === Tayyor. Inventarizatsiya uchun: ===
echo docker compose exec -T backend python scripts/inventory_demo_data.py --format markdown ^> demo-inventory.txt
echo type demo-inventory.txt
