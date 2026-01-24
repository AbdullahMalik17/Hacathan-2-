# Gmail Watcher Startup Script
# Quick launcher for Gmail monitoring only

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "📬 Gmail Watcher - Starting..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if token needs refresh (new permissions added)
$tokenPath = "config\token.json"
if (Test-Path $tokenPath) {
    $tokenAge = (Get-Item $tokenPath).LastWriteTime
    $daysSinceUpdate = (New-TimeSpan -Start $tokenAge -End (Get-Date)).Days

    if ($daysSinceUpdate -gt 7) {
        Write-Host "⚠️  Token is $daysSinceUpdate days old" -ForegroundColor Yellow
        Write-Host "💡 Consider re-authenticating for new features:" -ForegroundColor Yellow
        Write-Host "   Remove-Item config\token.json" -ForegroundColor Gray
        Write-Host ""
    }
} else {
    Write-Host "🔐 First run - will prompt for Google authentication" -ForegroundColor Yellow
    Write-Host ""
}

# Check credentials
if (-not (Test-Path "config\credentials.json")) {
    Write-Host "❌ ERROR: config\credentials.json not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Setup Instructions:" -ForegroundColor Yellow
    Write-Host "1. Go to Google Cloud Console" -ForegroundColor White
    Write-Host "2. Enable Gmail API" -ForegroundColor White
    Write-Host "3. Download credentials.json" -ForegroundColor White
    Write-Host "4. Place in config\credentials.json" -ForegroundColor White
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Ask about auto-reply
Write-Host "📤 Auto-Reply Configuration:" -ForegroundColor Yellow
Write-Host "   Enable auto-reply drafts for important emails? (y/N): " -ForegroundColor White -NoNewline
$response = Read-Host

$autoReply = "false"
if ($response -eq "y" -or $response -eq "Y") {
    $autoReply = "true"
    Write-Host "✅ Auto-reply ENABLED (creates drafts)" -ForegroundColor Green
} else {
    Write-Host "⏭️  Auto-reply DISABLED" -ForegroundColor Gray
}
Write-Host ""

# Set environment variable
$env:AUTO_REPLY_ENABLED = $autoReply

Write-Host "🚀 Starting Gmail Watcher..." -ForegroundColor Green
Write-Host ""
Write-Host "📊 Monitoring:" -ForegroundColor Cyan
Write-Host "   • Poll Interval: 60 seconds" -ForegroundColor White
Write-Host "   • Exclusion Label: NO_AI" -ForegroundColor White
Write-Host "   • Classifications: Important/Medium/Not Important" -ForegroundColor White
Write-Host "   • Auto-Reply: $autoReply" -ForegroundColor White
Write-Host ""
Write-Host "📂 Output:" -ForegroundColor Cyan
Write-Host "   • Task Files: Vault\Needs_Action\" -ForegroundColor White
Write-Host "   • Logs: Vault\Logs\gmail_watcher_*.log" -ForegroundColor White
Write-Host "   • Activity: Vault\Logs\$(Get-Date -Format 'yyyy-MM-dd').json" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Run the watcher
python src\watchers\gmail_watcher.py

# If it exits
Write-Host ""
Write-Host "📭 Gmail Watcher stopped" -ForegroundColor Yellow
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
