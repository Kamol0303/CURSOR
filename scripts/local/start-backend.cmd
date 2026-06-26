@echo off
cd /d "%~dp0..\.."
call "%~dp0_find-bash.cmd"
if errorlevel 1 exit /b 1
"%GIT_BASH%" "%~dp0start-backend.sh" %*
