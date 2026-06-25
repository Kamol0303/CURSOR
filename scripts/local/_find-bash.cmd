@echo off
setlocal EnableExtensions
if exist "C:\Program Files\Git\bin\bash.exe" (
  set "GIT_BASH=C:\Program Files\Git\bin\bash.exe"
  goto :done
)
if exist "C:\Program Files (x86)\Git\bin\bash.exe" (
  set "GIT_BASH=C:\Program Files (x86)\Git\bin\bash.exe"
  goto :done
)
where bash >nul 2>&1
if %ERRORLEVEL%==0 (
  for /f "delims=" %%i in ('where bash') do set "GIT_BASH=%%i" & goto :done
)
echo XATO: Git Bash topilmadi.
echo Git for Windows o'rnating: https://git-scm.com/download/win
exit /b 1
:done
endlocal & set "GIT_BASH=%GIT_BASH%"
exit /b 0
