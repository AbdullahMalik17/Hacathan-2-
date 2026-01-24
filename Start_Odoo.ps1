# Start Odoo Community Edition for Digital FTE
# Gold Tier Requirement: Odoo integration for business accounting

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Starting Odoo Community Edition   " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[1/5] Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "  ✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Docker not found or not running!" -ForegroundColor Red
    Write-Host "  Please install Docker Desktop and ensure it's running" -ForegroundColor Red
    Write-Host "  Download: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if docker-compose file exists
Write-Host ""
Write-Host "[2/5] Checking configuration..." -ForegroundColor Yellow
if (-Not (Test-Path "docker-compose.odoo.yml")) {
    Write-Host "  ✗ docker-compose.odoo.yml not found!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Configuration file found" -ForegroundColor Green

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "  ⚠ .env file not found, using defaults" -ForegroundColor Yellow
    Write-Host "  Copy config/.env.example to .env and configure" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Environment variables loaded" -ForegroundColor Green
}

# Start Odoo services
Write-Host ""
Write-Host "[3/5] Starting Odoo containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.odoo.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Failed to start Odoo!" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host ""
Write-Host "[4/5] Waiting for services to initialize..." -ForegroundColor Yellow
Write-Host "  This may take 30-60 seconds on first run..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# Check service status
$attempts = 0
$maxAttempts = 12
$ready = $false

while ($attempts -lt $maxAttempts -and -not $ready) {
    $attempts++
    Write-Host "  Attempt $attempts/$maxAttempts..." -ForegroundColor Gray

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8069/web/database/selector" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $ready = $true
            Write-Host "  ✓ Odoo is ready!" -ForegroundColor Green
        }
    } catch {
        Start-Sleep -Seconds 5
    }
}

if (-not $ready) {
    Write-Host "  ⚠ Odoo is starting but not responding yet" -ForegroundColor Yellow
    Write-Host "  Check logs: docker-compose -f docker-compose.odoo.yml logs -f" -ForegroundColor Yellow
}

# Display connection information
Write-Host ""
Write-Host "[5/5] Odoo Status" -ForegroundColor Yellow
docker-compose -f docker-compose.odoo.yml ps

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Odoo Started Successfully!        " -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Web Interface: http://localhost:8069" -ForegroundColor Cyan
Write-Host "🗄️  Database: digital_fte" -ForegroundColor Cyan
Write-Host "👤 Username: admin" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 First Time Setup:" -ForegroundColor Yellow
Write-Host "   1. Open http://localhost:8069 in browser" -ForegroundColor White
Write-Host "   2. Create database 'digital_fte'" -ForegroundColor White
Write-Host "   3. Set admin password" -ForegroundColor White
Write-Host "   4. Install: Accounting, Contacts, Invoicing" -ForegroundColor White
Write-Host "   5. Update .env with ODOO_PASSWORD" -ForegroundColor White
Write-Host ""
Write-Host "📚 Full documentation: docs/ODOO_SETUP.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Useful commands:" -ForegroundColor Yellow
Write-Host "   Stop:    docker-compose -f docker-compose.odoo.yml stop" -ForegroundColor White
Write-Host "   Restart: docker-compose -f docker-compose.odoo.yml restart" -ForegroundColor White
Write-Host "   Logs:    docker-compose -f docker-compose.odoo.yml logs -f odoo" -ForegroundColor White
Write-Host "   Down:    docker-compose -f docker-compose.odoo.yml down" -ForegroundColor White
Write-Host ""

# Open browser to Odoo
Write-Host "Opening Odoo in browser..." -ForegroundColor Gray
Start-Sleep -Seconds 2
Start-Process "http://localhost:8069"

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
