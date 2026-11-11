@echo off
setlocal
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\docker.ps1" -Action down %*
set "LAB_EXIT=%ERRORLEVEL%"
if not "%LAB_EXIT%"=="0" (
    echo.
    echo Falha ao parar. Leia a mensagem acima.
    if not "%LAB_NO_PAUSE%"=="1" pause
)
exit /b %LAB_EXIT%
