@echo off
REM TMB — git merge/conflict dan keyin repozitoriyani tiklash
REM Ishlatish: scripts\windows\recover-repo.cmd
cd /d "%~dp0..\.."

echo === 1. Merge bekor qilish (agar bor bo'lsa) ===
git merge --abort 2>nul

echo === 2. celerybeat-schedule tozalash ===
if exist backend\celerybeat-schedule del /f /q backend\celerybeat-schedule

echo === 3. origin/main ga toza reset ===
git fetch origin
git checkout main 2>nul
if errorlevel 1 git checkout -b main origin/main
git reset --hard origin/main

echo === 4. Conflict marker tekshiruvi ===
findstr /s /m /c:"<<<<<<<" docker-compose.yml backend\app\*.py 2>nul
if not errorlevel 1 (
  echo XATO: Hali conflict markerlar bor! Qo'lda tuzating.
  exit /b 1
)

echo === 5. Docker qayta ishga tushirish ===
call "%~dp0update-main.cmd"
