@echo off
REM ============================================================
REM Automated Task Runner with Git Pull
REM This batch file pulls latest code and runs the Python script
REM ============================================================

echo.
echo ============================================================
echo  Automated Task Runner
echo ============================================================
echo  Time: %date% %time%
echo ============================================================
echo.

REM Change to script directory
cd /d "%~dp0"
echo Current directory: %cd%
echo.

REM Pull latest changes from GitHub
echo [1/2] Pulling latest code from GitHub...
git pull
echo.

REM Check if pull was successful
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git pull failed!
    echo Please check your internet connection and Git setup.
    pause
    exit /b 1
)

REM Run the Python script
echo [2/2] Running Python script...
python daily_task.py
echo.

REM Check if script ran successfully
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python script failed!
    pause
    exit /b 1
)

echo ============================================================
echo  Task completed successfully!
echo ============================================================
echo.
echo Window will close in 10 seconds...
echo.

REM Wait 10 seconds so you can read the messages
ping 127.0.0.1 -n 11 > nul

