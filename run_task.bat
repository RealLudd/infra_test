@echo off
REM ============================================================
REM BPA Task Runner - Clean and Simple
REM ============================================================

REM Change to script directory
cd /d "%~dp0"

REM Sync with GitHub (silent)
git fetch origin > nul 2>&1
git pull > nul 2>&1

REM Auto-merge Claude branches (silent)
for /f "tokens=*" %%b in ('git branch -r 2^>nul ^| findstr /C:"origin/claude/"') do (
    git merge %%b --no-edit > nul 2>&1
)

REM Run the Python script (this shows the output)
python daily_task.py

REM Wait 10 seconds
ping 127.0.0.1 -n 11 > nul

