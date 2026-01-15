@echo off
REM Digital FTE Auto-Start Script
REM This script is registered with Windows Task Scheduler to run at user login

echo =================================================
echo Digital FTE Starting Up...
echo =================================================
echo.

REM Set the project directory (adjust if needed)
set "PROJECT_DIR=%~dp0..\.."
cd /d "%PROJECT_DIR%"

REM Log startup attempt
echo [%date% %time%] Digital FTE startup initiated >> "%PROJECT_DIR%\Vault\Logs\startup.log"

REM Activate virtual environment if it exists
if exist "%PROJECT_DIR%\venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "%PROJECT_DIR%\venv\Scripts\activate.bat"
) else if exist "%PROJECT_DIR%\.venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "%PROJECT_DIR%\.venv\Scripts\activate.bat"
)

REM Start the service manager (which manages all watchers)
echo Starting Service Manager...
start "Digital FTE Service Manager" /min python "%PROJECT_DIR%\src\service_manager.py"

REM Log success
echo [%date% %time%] Digital FTE Service Manager started >> "%PROJECT_DIR%\Vault\Logs\startup.log"

echo.
echo Digital FTE is now running in the background.
echo Check Vault\Logs\startup_log.md for service status.
echo.

REM Keep window open briefly to show status (optional - remove for silent startup)
timeout /t 5 /nobreak >nul
