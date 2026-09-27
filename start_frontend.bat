@echo off
echo ========================================
echo  Smart Waste System - Starting Frontend
echo ========================================
echo.

cd /d "%~dp0frontend"

echo Starting HTTP server for frontend...
echo.
echo Dashboard will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python -m http.server 8000

pause
