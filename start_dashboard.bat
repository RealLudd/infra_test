@echo off
REM ========================================================
REM Start CashWeb Dashboard Server
REM ========================================================
REM Starts the Flask web server in the background
REM ========================================================

echo.
echo ========================================================
echo   Starting CashWeb Dashboard Server
echo ========================================================
echo.

cd /d "%~dp0"

REM Check if already running
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo Dashboard is already running at http://localhost:5000
    echo.
    start http://localhost:5000
    pause
    exit /b 0
)

echo Starting Flask server...
echo.

REM Start Python Flask app in a new window (minimized)
start "CashWeb Dashboard" /MIN python app.py

REM Wait for server to start
timeout /t 5 /nobreak >nul

echo.
echo ========================================================
echo   Dashboard Started Successfully!
echo ========================================================
echo.
echo   URL: http://localhost:5000
echo.
echo   The server is running in a background window.
echo   To stop it, close the "CashWeb Dashboard" window
echo   or press Ctrl+C in that window.
echo ========================================================
echo.

REM Open browser
start http://localhost:5000

pause

