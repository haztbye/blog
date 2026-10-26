@echo off
REM ASCII only in this file.
REM Encrypt the study log, then publish the site.
REM (publish.bat already refreshes the log automatically; this wrapper is for
REM  when you want to publish ONLY because of a log update.)

chcp 65001 >nul
setlocal
cd /d "%~dp0..\.."

call tools\study-log\refresh.bat
if errorlevel 1 (
  echo.
  echo Encrypt step failed - nothing was published.
  pause
  exit /b 1
)

call publish.bat "chore: study log update"
exit /b %ERRORLEVEL%