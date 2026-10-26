@echo off
REM ASCII only in this file (Chinese text in .bat breaks under some code pages).
REM Set the passphrase used to encrypt the study log.
REM It is stored OUTSIDE the git repo: %USERPROFILE%\.huanhe-study-key
REM Asks twice and compares, so a typo cannot silently lock you out.

chcp 65001 >nul
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "function Ask($prompt) {" ^
  "  $p = Read-Host -AsSecureString $prompt;" ^
  "  $b = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($p);" ^
  "  $s = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($b);" ^
  "  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b);" ^
  "  return $s }" ^
  "$a = Ask 'New passphrase (typing is hidden)';" ^
  "if ($a.Length -lt 8) { Write-Host 'Too short: at least 8 characters.' -ForegroundColor Red; exit 1 }" ^
  "$b = Ask 'Type it again to confirm';" ^
  "if ($a -cne $b) { Write-Host 'The two entries differ - nothing was saved. Run this again.' -ForegroundColor Red; exit 1 }" ^
  "$f = Join-Path $env:USERPROFILE '.huanhe-study-key';" ^
  "Set-Content -LiteralPath $f -Value $a -Encoding UTF8 -NoNewline;" ^
  "Write-Host ''; Write-Host ('Saved to: ' + $f) -ForegroundColor Green;" ^
  "Write-Host ('Length: ' + $a.Length + ' characters');" ^
  "Write-Host 'Next: run publish-log.bat (re-encrypt) then verify-key.bat (check it).'"

if errorlevel 1 (
  echo.
  echo FAILED - nothing was saved.
)

echo.
pause
exit /b 0