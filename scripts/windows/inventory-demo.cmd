@echo off
REM Demo ma'lumot inventarizatsiyasi (faqat o'qish, hech narsa o'chirmaydi)
cd /d "%~dp0..\.."

docker compose ps | findstr /i "backend" | findstr /i "Up" >nul
if errorlevel 1 (
  echo XATO: Backend ishlamayapti. Avval: scripts\start.cmd
  exit /b 1
)

docker compose exec -T backend python scripts/inventory_demo_data.py --format markdown > demo-inventory.txt
if errorlevel 1 (
  echo XATO: Skript ishlamadi. demo-inventory.txt ni tekshiring.
  exit /b 1
)

echo Yozildi: demo-inventory.txt
type demo-inventory.txt
