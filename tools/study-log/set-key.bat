@echo off
REM ASCII only in this file (Chinese text in .bat breaks under some code pages).
REM Set the passphrase used to encrypt the study log.
REM It is stored OUTSIDE the git repo: %USERPROFILE%\.huanhe-study-key

chcp 65001 >nul
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p = Read-Host -AsSecureString 'Passphrase for your study log (typing is hidden)';" ^
  "$b = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($p);" ^
  "$s = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($b);" ^
  "[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b);" ^
  "if ($s.Length -lt 8) { Write-Host 'Too short: at least 8 characters.' -ForegroundColor Red; exit 1 }" ^
  "$f = Join-Path $env:USERPROFILE '.huanhe-study-key';" ^
  "Set-Content -LiteralPath $f -Value $s -Encoding UTF8 -NoNewline;" ^
  "Write-Host ''; Write-Host ('Saved to: ' + $f) -ForegroundColor Green;" ^
  "Write-Host 'Keep it in a password manager - without it the log cannot be decrypted.'"

if errorlevel 1 (
  echo.
  echo FAILED - nothing was saved.
)

echo.
pause
exit /b 0