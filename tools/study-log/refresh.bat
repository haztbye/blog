@echo off
REM ASCII only in this file.
REM Re-encrypt the study log from the plaintext file outside the repo.
REM Exit code 0 = success, 1 = failed (caller may ignore it).

chcp 65001 >nul
setlocal
cd /d "%~dp0..\.."

set "PLAIN=..\study-log-private\kaoyan-log.md"
set "KEY=%USERPROFILE%\.huanhe-study-key"

if not exist "%PLAIN%" (
  echo [study-log] plaintext not found: %PLAIN%
  exit /b 1
)
if not exist "%KEY%" (
  echo [study-log] no passphrase file: run tools\study-log\set-key.bat first
  exit /b 1
)

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
  echo [study-log] no Python with the 'cryptography' package found.
  echo             set STUDY_LOG_PY to a python.exe and retry.
  exit /b 1
)

"%PY%" tools\study-log\encrypt_log.py
exit /b %ERRORLEVEL%