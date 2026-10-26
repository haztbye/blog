@echo off
REM ASCII only in this file.
REM Encrypt the study log (plaintext stays outside the repo) and publish the site.

chcp 65001 >nul
setlocal
cd /d "%~dp0..\.."

set "PY="
for %%C in (
  "%STUDY_LOG_PY%"
  "%USERPROFILE%\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
  "py -3"
  "python"
) do (
  if not defined PY (
    %%~C -c "import cryptography" >nul 2>&1
    if not errorlevel 1 set "PY=%%~C"
  )
)

if not defined PY (
  echo No Python with the 'cryptography' package found.
  echo Set STUDY_LOG_PY to a suitable python.exe and run again.
  pause
  exit /b 1
)

echo Using interpreter: %PY%
"%PY%" tools\study-log\encrypt_log.py
if errorlevel 1 (
  echo.
  echo Encrypt step failed - nothing was published.
  pause
  exit /b 1
)

call publish.bat "chore: study log update"
exit /b %ERRORLEVEL%