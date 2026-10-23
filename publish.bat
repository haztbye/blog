@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

REM ASCII only in this file: cmd batch parsing breaks with UTF-8 Chinese under chcp 65001.
REM One-click publish: git commit -> push to GitHub -> build & deploy to server.
REM Usage:  publish.bat            (default commit message)
REM         publish.bat "message"  (custom commit message)

set "MSG=%~1"
if "%MSG%"=="" set "MSG=update: publish from local"

echo ================================================
echo  [1/3] git add + commit
echo ================================================
git add -A
if errorlevel 1 goto :fail

git diff --cached --quiet
if %ERRORLEVEL%==0 (
    echo   nothing to commit, skipping
) else (
    git commit -m "%MSG%"
    if errorlevel 1 goto :fail
)

echo.
echo ================================================
echo  [2/3] git push
echo ================================================
git push
if errorlevel 1 goto :fail

echo.
echo ================================================
echo  [3/3] build + deploy
echo ================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy-blog.ps1"
if errorlevel 1 goto :fail

echo.
echo All done.
pause
exit /b 0

:fail
echo.
echo FAILED - see messages above.
pause
exit /b 1
