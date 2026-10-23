@echo off
chcp 65001 >nul
setlocal

REM ASCII only in this file: cmd batch parsing breaks with UTF-8 Chinese under chcp 65001.
REM All user-facing Chinese text is printed by deploy-blog.ps1 instead.

set "PS1=%~dp0deploy-blog.ps1"

if not exist "%PS1%" (
    echo [ERROR] deploy-blog.ps1 not found next to this .bat file.
    pause
    exit /b 1
)

where pwsh >nul 2>nul
if %ERRORLEVEL%==0 (
    pwsh -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %*
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %*
)

set "RC=%ERRORLEVEL%"
echo.
if not "%~1"=="" (
    echo Options: -Full upload all ^| -NoDelete keep extra remote files ^| -DryRun preview only
    echo.
)
pause
exit /b %RC%
