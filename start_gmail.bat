@echo off
REM Simple batch file to start Gmail Watcher
REM For users who prefer batch files over PowerShell

echo ================================================
echo Gmail Watcher - Starting...
echo ================================================
echo.

REM Check credentials
if not exist "config\credentials.json" (
    echo ERROR: config\credentials.json not found!
    echo.
    echo Setup Instructions:
    echo 1. Go to Google Cloud Console
    echo 2. Enable Gmail API
    echo 3. Download credentials.json
    echo 4. Place in config\credentials.json
    echo.
    pause
    exit /b 1
)

echo Starting Gmail Watcher...
echo.
echo Press Ctrl+C to stop
echo ================================================
echo.

REM Run the watcher
python src\watchers\gmail_watcher.py

echo.
echo Gmail Watcher stopped
pause
