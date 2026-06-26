@echo off
REM Barcha demo login va parollarni terminalda ko'rsatish
echo.
echo ============================================================
echo   TMB DEMO LOGINLAR (faqat dev/staging — production emas)
echo ============================================================
echo.
echo   super_admin        admin.tmb              Tmb#2026Admin!
echo                      MFA: ha — seed chiqaradi TOTP QR
echo.
echo   hokimiyat_operator operator.hokimiyat       Hokim#Op2026!
echo                      MFA: ha — seed chiqaradi TOTP QR
echo.
echo   center_director    director.aspect          Direktor#2026!
echo                      MFA: ha — seed chiqarida TOTP QR
echo.
echo   center_admin       admin.aspect             CenterAdmin#26!
echo                      MFA: yo'q
echo.
echo   teacher            teacher.dilnoza          Teach#Dil2026!
echo                      MFA: yo'q
echo.
echo   student            student.sardor           Student#2026!
echo                      MFA: yo'q
echo.
echo   auditor            auditor.tuman            Audit#Check26!
echo                      MFA: yo'q
echo.
echo   parent/guardian    +998901234567            OTP konsolda (SMS yo'q)
echo.
echo   External API       GET /api/v1/external/aggregate-stats
echo                      Header: X-Api-Key: ^(seed chiqaradi yoki api_keys jadvali^)
echo.
echo   URL dev:            http://localhost:3000
echo   URL staging:        https://tamor.staging.local
echo ============================================================
echo.
