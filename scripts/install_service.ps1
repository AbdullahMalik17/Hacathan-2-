# scripts/install_service.ps1
# Registers the Digital FTE Service Manager to run at user logon.
# Run this script as Administrator.

$ErrorActionPreference = "Stop"

# Get project root (assumes this script is in /scripts)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$ServiceManagerScript = Join-Path $ProjectRoot "src\service_manager.py"
$TaskName = "DigitalFTE_ServiceManager"

Write-Host "Project Root: $ProjectRoot"
Write-Host "Python Path:  $VenvPython"
Write-Host "Manager Path: $ServiceManagerScript"

# Verify paths
if (-not (Test-Path $VenvPython)) {
    Write-Error "Virtual environment python not found at $VenvPython. Please set up the .venv first."
}
if (-not (Test-Path $ServiceManagerScript)) {
    Write-Error "Service manager script not found at $ServiceManagerScript."
}

# Create the action
# We run pythonw.exe (windowless) or python.exe (with window). 
# For a background task, pythonw.exe is better, but for debugging, python.exe is useful.
# Let's use python.exe for now so the user can see it running, 
# or maybe better: execute a hidden command.
# The spec suggested: -Execute "cmd.exe" -Argument "/c $ScriptPath"
# We will execute python directly.

$Action = New-ScheduledTaskAction `
    -Execute $VenvPython `
    -Argument """$ServiceManagerScript""" `
    -WorkingDirectory $ProjectRoot

# Create the trigger (At Logon)
$Trigger = New-ScheduledTaskTrigger -AtLogon

# Create settings (Allow starting if on battery, etc.)
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Days 365) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

# Register the task
Write-Host "Registering Scheduled Task: $TaskName..."

try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Description "Manages Digital FTE services (Orchestrator, Watchers) at startup." `
        -Force
    
    Write-Host "Success! The Digital FTE service will start automatically when you log in."
    Write-Host "To start it immediately, run: Start-ScheduledTask -TaskName '$TaskName'"
} catch {
    Write-Error "Failed to register task. Ensure you are running PowerShell as Administrator. Details: $_"
}
