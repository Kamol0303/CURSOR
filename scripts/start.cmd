@echo off
REM TMB — Docker orqali ishga tushirish (Windows CMD)
REM   scripts\start.cmd          — dev (localhost:3000)
REM   scripts\start.cmd staging  — HTTPS staging
cd /d "%~dp0.."

where docker >nul 2>&1
if errorlevel 1 (
  echo XATO: Docker topilmadi.
  echo Docker Desktop o'rnating va ishga tushiring:
  echo   https://docs.docker.com/desktop/setup/install/windows-install/
  exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
  echo XATO: Docker Desktop ishlamayapti. Ilovani oching va kuting.
  exit /b 1
)

set "MODE=dev"
if /I "%~1"=="staging" set "MODE=staging"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %MODE%
