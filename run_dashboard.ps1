# Pewbeam UK Church Outreach Hub Launcher
Write-Host "====================================================" -ForegroundColor DarkYellow
Write-Host "⚡ Starting Pewbeam UK Church Outreach Hub..." -ForegroundColor Yellow
Write-Host "👉 Dashboard: http://127.0.0.1:8080" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor DarkYellow

Set-Location -Path $PSScriptRoot
Start-Process "http://127.0.0.1:8080"
python app.py
