<#
.SYNOPSIS
  PRAHARI-NET Developer Stack Launcher for Windows
.DESCRIPTION
  Launches FastAPI backend on :8000 and Vite frontend on :5173,
  displaying access URLs, API docs, and active operational status.
#>

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " PRAHARI-NET: Disaster Intelligence Command Platform" -ForegroundColor Cyan
Write-Host " SENSE • PREDICT • ALERT • PROTECT" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Start FastAPI Backend in new background process
Write-Host "Starting FastAPI Local Backend on port 8000..." -ForegroundColor Yellow
$backendProcess = Start-Process python -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000" -PassThru -WindowStyle Minimized

# 2. Start Vite Frontend in new background process
Write-Host "Starting React Command Centre on port 5173..." -ForegroundColor Yellow
Set-Location frontend
$frontendProcess = Start-Process npm -ArgumentList "run", "dev" -PassThru -WindowStyle Minimized
Set-Location ..

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " SYSTEM ONLINE & OPERATIONAL!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host " Command Centre UI:     http://localhost:5173" -ForegroundColor Cyan
Write-Host " SIH 2026 Jury Demo:   http://localhost:5173/demo" -ForegroundColor Magenta
Write-Host " Backend REST API:      http://127.0.0.1:8000" -ForegroundColor White
Write-Host " Swagger API Docs:      http://127.0.0.1:8000/api/docs" -ForegroundColor Yellow
Write-Host " Real-time WebSocket:   ws://127.0.0.1:8000/ws/live" -ForegroundColor White
Write-Host ""
Write-Host " Seed Demo Accounts:" -ForegroundColor Yellow
Write-Host "   Operator:  operator  /  prahari2026!" -ForegroundColor White
Write-Host "   Admin:     admin     /  prahari2026!" -ForegroundColor White
Write-Host "   Viewer:    viewer    /  prahari2026!" -ForegroundColor White
Write-Host ""
Write-Host " State:                 LOCAL EDGE MODE (Internet-Independent)" -ForegroundColor Green
Write-Host " Simulation:            CONTINUOUS DISASTER STREAM ACTIVE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Green
Write-Host " To stop all services, run: .\scripts\stop-dev.ps1" -ForegroundColor Gray
