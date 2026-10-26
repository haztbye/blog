@echo off
REM ASCII only in this file.
REM Check whether the passphrase you remember can unlock the current ciphertext.

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
  echo No Python with the 'cryptography' package found. Set STUDY_LOG_PY and retry.
  pause
  exit /b 1
)

echo.
echo [1] check the passphrase stored on this machine
"%PY%" tools\study-log\verify_key.py
echo.
echo [2] type a passphrase to check it (typing is hidden)
"%PY%" tools\study-log\verify_key.py --ask

echo.
pause
exit /b 0