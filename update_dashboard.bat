@echo off
REM ========================================================
REM CashWeb Dashboard Update Script
REM ========================================================
REM This script refreshes the dashboard data by:
REM 1. Checking if the Flask app is running
REM 2. If not running, starts the Flask app
REM 3. Opens the dashboard in your default browser
REM ========================================================

echo.
echo ========================================================
echo   CashWeb Dashboard Update
echo ========================================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher
    pause
    exit /b 1
)

REM Check if Flask is running on port 5000
echo Checking if dashboard is running...
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1

if errorlevel 1 (
    echo Dashboard is not running. Starting Flask app...
    echo.
    echo ========================================================
    echo   Starting CashWeb Dashboard Server
    echo ========================================================
    echo.
    echo The dashboard will be available at: http://localhost:5000
    echo.
    echo Press Ctrl+C to stop the server when you're done.
    echo ========================================================
    echo.
    
    REM Start Flask in the foreground
    python app.py
) else (
    echo Dashboard is already running!
    echo.
    echo Opening dashboard in browser...
    start http://localhost:5000
    echo.
    echo ========================================================
    echo Dashboard opened at: http://localhost:5000
    echo ========================================================
    echo.
    echo To refresh the data:
    echo   1. Click the period buttons (Today/Week/Month/Quarter)
    echo   2. Or press F5 to refresh the page
    echo.
    echo Company Status and Recent Transactions auto-refresh
    echo every 5 minutes.
    echo ========================================================
    echo.
)

pause

