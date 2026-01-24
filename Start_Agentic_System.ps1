# Abdullah Junior - Agentic Intelligence System Startup
# Run this script to start the full system with mobile notifications

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Abdullah Junior - Agentic Intelligence  " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
$pythonPath = "python"
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonPath = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonPath = "python3"
} else {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    exit 1
}

# Set working directory
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "[1/4] Installing dependencies..." -ForegroundColor Yellow
& $pythonPath -m pip install -r requirements.txt -q

Write-Host "[2/4] Setting up push notifications..." -ForegroundColor Yellow
$vapidFile = "config/push_notifications/vapid_keys.json"
if (-not (Test-Path $vapidFile)) {
    Write-Host "  Generating VAPID keys for push notifications..."
    & $pythonPath scripts/setup_push_notifications.py
}

Write-Host "[3/4] Starting API Server..." -ForegroundColor Yellow
$apiJob = Start-Job -ScriptBlock {
    param($root, $python)
    Set-Location $root
    & $python -m uvicorn src.api_server:app --host 0.0.0.0 --port 8000
} -ArgumentList $projectRoot, $pythonPath

Write-Host "  API Server started on http://localhost:8000" -ForegroundColor Green

Write-Host "[4/4] Starting Orchestrator with Agentic Intelligence..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# Set environment variables
$env:FTE_ROLE = "local"
$env:AGENT_ID = "local-agentic-01"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  System Started Successfully!            " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services running:" -ForegroundColor White
Write-Host "  - API Server:    http://localhost:8000" -ForegroundColor White
Write-Host "  - Dashboard:     http://localhost:3000 (start frontend separately)" -ForegroundColor White
Write-Host "  - Orchestrator:  Running with Agentic Intelligence" -ForegroundColor White
Write-Host ""
Write-Host "Mobile Setup:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:3000 on your phone" -ForegroundColor White
Write-Host "  2. Add to Home Screen (Install PWA)" -ForegroundColor White
Write-Host "  3. Enable notifications when prompted" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop..." -ForegroundColor Gray

# Run orchestrator in foreground
try {
    Set-Location "$projectRoot/src"
    & $pythonPath -c "
import sys
sys.path.insert(0, '..')
from orchestrator import DigitalFTEOrchestrator
orch = DigitalFTEOrchestrator(enable_agentic=True, enable_push=True)
orch.run()
"
} finally {
    # Cleanup
    Stop-Job $apiJob -ErrorAction SilentlyContinue
    Remove-Job $apiJob -ErrorAction SilentlyContinue
    Write-Host "System stopped." -ForegroundColor Yellow
}
