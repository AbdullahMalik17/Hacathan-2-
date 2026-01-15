# Digital FTE Auto-Start Installation Script
# Run this script as Administrator to register Digital FTE to start on login

param(
    [switch]$Uninstall,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Configuration
$TaskName = "DigitalFTE_AutoStart"
$TaskDescription = "Starts Digital FTE watchers and orchestrator on user login"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$StartupScript = Join-Path $PSScriptRoot "start_digital_fte.bat"
$LogPath = Join-Path $ProjectRoot "Vault\Logs"

# Ensure log directory exists
if (-not (Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
}

$InstallLog = Join-Path $LogPath "autostart_install.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Write-Host $logEntry
    Add-Content -Path $InstallLog -Value $logEntry
}

function Test-AdminPrivileges {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Remove-ExistingTask {
    $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Log "Removing existing task: $TaskName"
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Log "Existing task removed"
    }
}

function Install-AutoStart {
    Write-Log "=========================================="
    Write-Log "Digital FTE Auto-Start Installation"
    Write-Log "=========================================="

    # Check if startup script exists
    if (-not (Test-Path $StartupScript)) {
        Write-Log "ERROR: Startup script not found at: $StartupScript"
        throw "Startup script not found"
    }

    # Remove existing task if force flag is set
    if ($Force) {
        Remove-ExistingTask
    }

    # Check if task already exists
    $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Log "Task '$TaskName' already exists. Use -Force to reinstall."
        return
    }

    Write-Log "Creating scheduled task: $TaskName"

    # Create the action
    $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$StartupScript`"" -WorkingDirectory $ProjectRoot

    # Create the trigger (at user logon)
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

    # Create settings
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 1)

    # Create principal (run as current user)
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

    # Register the task
    try {
        Register-ScheduledTask `
            -TaskName $TaskName `
            -Description $TaskDescription `
            -Action $action `
            -Trigger $trigger `
            -Settings $settings `
            -Principal $principal

        Write-Log "SUCCESS: Task '$TaskName' registered successfully"
        Write-Log "Digital FTE will now start automatically when you log in"
    }
    catch {
        Write-Log "ERROR: Failed to register task: $_"
        throw
    }

    # Also add to Monday CEO Briefing schedule
    Install-BriefingSchedule

    Write-Log "=========================================="
    Write-Log "Installation Complete"
    Write-Log "=========================================="
}

function Install-BriefingSchedule {
    $BriefingTaskName = "DigitalFTE_WeeklyBriefing"

    Write-Log "Setting up Weekly CEO Briefing schedule..."

    # Remove existing briefing task
    $existingBriefing = Get-ScheduledTask -TaskName $BriefingTaskName -ErrorAction SilentlyContinue
    if ($existingBriefing) {
        Unregister-ScheduledTask -TaskName $BriefingTaskName -Confirm:$false
    }

    # Find Python executable
    $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $pythonPath) {
        Write-Log "WARNING: Python not found in PATH. Briefing schedule not created."
        return
    }

    $briefingScript = Join-Path $ProjectRoot "src\reports\ceo_briefing.py"

    # Create action for briefing
    $briefingAction = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$briefingScript`"" -WorkingDirectory $ProjectRoot

    # Create trigger for Monday 8:00 AM
    $briefingTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "08:00"

    # Create settings
    $briefingSettings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable

    # Register briefing task
    try {
        Register-ScheduledTask `
            -TaskName $BriefingTaskName `
            -Description "Generates weekly CEO briefing report every Monday at 8 AM" `
            -Action $briefingAction `
            -Trigger $briefingTrigger `
            -Settings $briefingSettings

        Write-Log "SUCCESS: Weekly briefing schedule created (Mondays at 8:00 AM)"
    }
    catch {
        Write-Log "WARNING: Failed to create briefing schedule: $_"
    }
}

function Uninstall-AutoStart {
    Write-Log "=========================================="
    Write-Log "Digital FTE Auto-Start Removal"
    Write-Log "=========================================="

    # Remove main task
    Remove-ExistingTask

    # Remove briefing task
    $BriefingTaskName = "DigitalFTE_WeeklyBriefing"
    $existingBriefing = Get-ScheduledTask -TaskName $BriefingTaskName -ErrorAction SilentlyContinue
    if ($existingBriefing) {
        Write-Log "Removing briefing task: $BriefingTaskName"
        Unregister-ScheduledTask -TaskName $BriefingTaskName -Confirm:$false
        Write-Log "Briefing task removed"
    }

    Write-Log "=========================================="
    Write-Log "Uninstallation Complete"
    Write-Log "=========================================="
}

# Main execution
try {
    if ($Uninstall) {
        Uninstall-AutoStart
    }
    else {
        Install-AutoStart
    }
}
catch {
    Write-Log "FATAL ERROR: $_"
    exit 1
}
