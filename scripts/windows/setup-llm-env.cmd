@echo off
REM TMB — LLM API kalitlarini .env fayliga yozish (gitga kirmaydi)
REM Ishlatish: scripts\windows\setup-llm-env.cmd
cd /d "%~dp0..\.."

if not exist .env (
  echo .env topilmadi — .env.example dan nusxa olinmoqda...
  copy /y .env.example .env >nul
)

echo.
echo === TMB LLM sozlash ===
echo Kalitlarni faqat .env fayliga yozamiz — gitga COMMIT QILMANG!
echo.
echo 1) BazaarLink (asosiy): sk-bl-...
echo 2) Gemini (zaxira 1): Google AI Studio
echo 3) Mistral (zaxira 2): console.mistral.ai
echo.
set /p BAZAAR_KEY="BazaarLink LLM_API_KEY (bo'sh qoldirish mumkin): "
set /p GEMINI_KEY="Gemini GEMINI_API_KEY (bo'sh qoldirish mumkin): "
set /p MISTRAL_KEY="Mistral MISTRAL_API_KEY (bo'sh qoldirish mumkin): "

if not "%BAZAAR_KEY%"=="" (
  powershell -NoProfile -Command "(Get-Content .env) -replace '^LLM_API_KEY=.*','LLM_API_KEY=%BAZAAR_KEY%' | Set-Content .env"
  findstr /b "LLM_API_KEY=" .env >nul || echo LLM_API_KEY=%BAZAAR_KEY%>>.env
)

if not "%GEMINI_KEY%"=="" (
  powershell -NoProfile -Command "(Get-Content .env) -replace '^GEMINI_API_KEY=.*','GEMINI_API_KEY=%GEMINI_KEY%' | Set-Content .env"
  findstr /b "GEMINI_API_KEY=" .env >nul || echo GEMINI_API_KEY=%GEMINI_KEY%>>.env
)

if not "%MISTRAL_KEY%"=="" (
  powershell -NoProfile -Command "(Get-Content .env) -replace '^MISTRAL_API_KEY=.*','MISTRAL_API_KEY=%MISTRAL_KEY%' | Set-Content .env"
  findstr /b "MISTRAL_API_KEY=" .env >nul || echo MISTRAL_API_KEY=%MISTRAL_KEY%>>.env
)

echo.
echo Tayyor. Keyin: scripts\windows\update-main.cmd
echo.
echo XAVFSIZLIK: chat orqali yuborilgan kalitlarni provider dashboarddan YANGILANG!
