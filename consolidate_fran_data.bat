@echo off
REM ========================================================
REM FRAN Daily Data Consolidation Script
REM ========================================================
REM This script collects today's FRAN output and adds it
REM to the consolidated database. It will replace any
REM existing records for the same date.
REM ========================================================

echo.
echo ========================================================
echo   FRAN Daily Data Consolidation
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

REM Check if required packages are installed
echo Checking dependencies...
pip show pandas >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
)

echo.
echo Starting FRAN consolidation...
echo.

REM Run the consolidation script
python consolidate_fran_data.py

REM The script will handle the pause and exit


