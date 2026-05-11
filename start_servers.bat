@echo off
title PGDOST Server Launcher
color 0A

echo.
echo  ==========================================
echo   PGDOST - Starting All Servers
echo  ==========================================
echo.

:: Start Django Backend
echo  [1/2] Starting Django Backend on http://127.0.0.1:8000 ...
start "PGDOST Backend (Django)" cmd /k "cd /d c:\Users\aravi\OneDrive\Documents\newfinalyearproject - Copy (3)\backend && venv\Scripts\python.exe manage.py runserver"

:: Wait 2 seconds using ping (works when stdin is redirected)
ping 127.0.0.1 -n 3 >NUL 2>&1

:: Start Frontend Server
echo  [2/2] Starting Frontend Server on http://localhost:5500 ...
start "PGDOST Frontend (HTTP)" cmd /k "cd /d c:\Users\aravi\OneDrive\Documents\newfinalyearproject - Copy (3)\frontend && python -m http.server 5500"

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

