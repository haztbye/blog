@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

REM ASCII only in this file.
REM Publish = commit + push. GitHub Actions builds and deploys to the server.
REM Usage: publish.bat            (default commit message)
REM        publish.bat "message"  (custom commit message)
REM No local changes? It still makes an empty commit, so the site rebuilds
REM (useful after adding songs to the NetEase playlist).

set "MSG=%~1"
if "%MSG%"=="" set "MSG=update: publish from local"

echo [1/3] git add
git add -A
if errorlevel 1 goto :fail

git diff --cached --quiet
if %ERRORLEVEL%==0 (
    echo   nothing changed - empty commit to trigger a fresh build
    git commit --allow-empty -m "chore: refresh site data"
    if errorlevel 1 goto :fail
    goto :push
)

echo [2/3] git commit
git commit -m "%MSG%"
if errorlevel 1 goto :fail

:push
echo [3/3] git push
git push
if errorlevel 1 goto :fail

echo.
echo Pushed. GitHub Actions is now building and deploying.
echo Check: https://github.com/haztbye/blog/actions
pause
exit /b 0

:fail
echo.
echo FAILED - see messages above.
pause
exit /b 1
