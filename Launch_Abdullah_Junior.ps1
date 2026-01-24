Write-Host "Starting Abdullah Junior System..."

$VenvPath = ".venv\Scripts\activate.ps1"
if (Test-Path $VenvPath) {
    Write-Host "Activating Python Virtual Environment..."
}

Write-Host "Starting Background Services..."
Start-Process powershell -ArgumentList "-NoProfile", "-Command", "& { . .venv\Scripts\activate.ps1; python src/service_manager.py --start-all }" -WindowStyle Minimized

Write-Host "Starting Web Dashboard..."
if (Test-Path "frontend/node_modules") {
    Start-Process powershell -ArgumentList "-NoProfile", "-Command", "cd frontend; npm run dev" -WindowStyle Minimized
    Write-Host "Dashboard: http://localhost:3000"
}

Write-Host "All systems initiated."
