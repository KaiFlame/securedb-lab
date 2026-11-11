@echo off
setlocal
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\docker.ps1" -Action test %*
set "LAB_EXIT=%ERRORLEVEL%"
echo.
echo Testes encerrados com codigo %LAB_EXIT%.
if not "%LAB_NO_PAUSE%"=="1" pause
exit /b %LAB_EXIT%
