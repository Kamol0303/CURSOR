@echo off
REM TMB — .env.staging yaratish (Windows)
REM Ishlatish: scripts\windows\setup-staging-env.cmd
cd /d "%~dp0..\.."

if exist .env.staging (
  echo .env.staging allaqachon mavjud — o'zgartirilmadi.
  exit /b 0
)

copy /Y .env.staging.example .env.staging >nul
if errorlevel 1 (
  echo XATO: .env.staging.example topilmadi.
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$dbPass = 'TmbStaging' + (-join ((48..57) + (65..90) | Get-Random -Count 8 | ForEach-Object { [char]$_ })); ^
   $secret = 'dev-staging-secret-32chars-min!!'; ^
   (Get-Content .env.staging) ^
     -replace 'CHANGE_ME_staging_db_password', $dbPass ^
     -replace 'CHANGE_ME_32_CHARS_MINIMUM_______', $secret | ^
   Set-Content .env.staging -Encoding UTF8; ^
   Write-Host '.env.staging yaratildi. POSTGRES_PASSWORD va DATABASE_URL sinxron.'"

echo.
echo Keyingi qadam: TLS sertifikat (bir marta)
echo   bash infra/nginx/generate-dev-certs.sh
echo yoki Git Bash / WSL da ishga tushiring.
echo.
echo Staging ishga tushirish:
echo   scripts\windows\staging-up.cmd
