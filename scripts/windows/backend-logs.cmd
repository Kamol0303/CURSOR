@echo off
REM Backend xatosini diagnostika qilish
cd /d "%~dp0..\.."

echo === Konteyner holati ===
docker compose ps -a

echo.
echo === Backend oxirgi 120 qator log ===
docker compose logs backend --tail 120

echo.
echo === Migration holati (agar backend ishlayotgan bo'lsa) ===
docker compose exec -T backend alembic current 2>nul
if errorlevel 1 echo (backend ishlamayapti — yuqoridagi loglarni o'qing)

echo.
echo === Tez yechim (BAZA O'CHADI - faqat dev) ===
echo docker compose down -v
echo docker compose build --no-cache backend
echo scripts\start.cmd
