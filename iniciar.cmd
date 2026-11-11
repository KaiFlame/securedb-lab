@echo off
setlocal
rem ExecutionPolicy Bypass applies only to this child process; no system policy changes.
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\docker.ps1" -Action up %*
set "LAB_EXIT=%ERRORLEVEL%"
if not "%LAB_EXIT%"=="0" (
    echo.
    echo Falha ao iniciar. Leia a mensagem acima.
    if not "%LAB_NO_PAUSE%"=="1" pause
)
exit /b %LAB_EXIT%
