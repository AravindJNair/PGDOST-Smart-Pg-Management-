@echo off
title PGDOST Server Launcher
color 0A

setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0

echo.
echo  ==========================================
echo   PGDOST - Starting All Servers
echo  ==========================================
echo.

:: Start Django Backend
echo  [1/2] Starting Django Backend on http://127.0.0.1:8000 ...
cd /d "%SCRIPT_DIR%backend"
if exist "%SCRIPT_DIR%backend\venv\Scripts\python.exe" (
    set "PYTHON=%SCRIPT_DIR%backend\venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)
start "PGDOST Backend (Django)" /D "%SCRIPT_DIR%backend" cmd /k "%PYTHON% manage.py runserver"

:: Wait 2 seconds using ping (works when stdin is redirected)
ping 127.0.0.1 -n 3 >NUL 2>&1

:: Start Frontend Server
echo  [2/2] Starting Frontend Server on http://localhost:5500 ...
start "PGDOST Frontend (HTTP)" /D "%SCRIPT_DIR%frontend" cmd /k "python -m http.server 5500"

:: Wait 2 seconds then open browser
ping 127.0.0.1 -n 3 >NUL 2>&1

echo.
echo  ==========================================
echo   Both servers are running!
echo  ==========================================
echo.
echo   Website Home    : http://localhost:5500/pages/index.html
echo   Resident Login  : http://localhost:5500/pages/login.html
echo   Owner Login     : http://localhost:5500/pages/owner-login.html
echo   Admin Portal    : http://localhost:5500/pages/admin-portal/login.html
echo   Django API      : http://127.0.0.1:8000/api/
echo.
echo  Opening website in browser...
start http://localhost:5500/pages/index.html

echo  All done! You can close this window.
endlocal

