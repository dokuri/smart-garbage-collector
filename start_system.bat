@echo off
echo.
echo  ========================================================
echo  🌍 Smart Waste Management System - Starting...
echo  ========================================================
echo.
echo  This system monitors bins, detects methane, and
echo  optimizes collection routes for environmental impact.
echo.

:: Start backend in new window
echo  [1/3] Starting Backend Server...
start "Smart Waste Backend" cmd /k "cd /d %~dp0backend && python app.py"

:: Wait for backend to initialize
timeout /t 4 /nobreak > nul

echo  [2/3] Backend running on http://localhost:5000
echo.
echo  [3/3] Opening Dashboard...

:: Open browser to backend (which serves frontend)
start http://localhost:5000

echo.
echo  ========================================================
echo  ✅ System Started Successfully!
echo  ========================================================
echo.
echo  📊 Dashboard: http://localhost:5000
echo.
echo  🎮 Quick Guide:
echo     1. Click "Demo Scenario" to create test data
echo     2. Click locations on map to view bins
echo     3. Click "Optimize Route" to see AI routing
echo.
echo  🔧 Hardware: Connect ESP32 to see real sensor data
echo     (A1_WET bin will show live readings)
echo.
echo  Press any key to close this window...
pause > nul
echo.
echo Close terminal windows to stop servers.
pause
