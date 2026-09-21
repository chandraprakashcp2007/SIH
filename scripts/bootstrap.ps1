<#
.SYNOPSIS
  PRAHARI-NET Automated Setup & Bootstrap Script for Windows PowerShell
.DESCRIPTION
  Installs required Python backend dependencies, npm frontend packages,
  creates SQLite database, and seeds demo operational credentials and nodes.
#>

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " PRAHARI-NET: System Bootstrap & Initialization" -ForegroundColor Cyan
Write-Host " Smart India Hackathon 2026 - Problem Statement SIH26178" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Environment file check
if (-not (Test-Path ".env")) {
    Write-Host "[1/4] Creating local .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
} else {
    Write-Host "[1/4] Local .env already exists. Preserved." -ForegroundColor Green
}

# 2. Python Packages
Write-Host "[2/4] Verifying Python backend dependencies..." -ForegroundColor Yellow
python -m pip install -r backend/requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Pip install reported issues. Retrying core dependencies..." -ForegroundColor Yellow
    python -m pip install fastapi uvicorn pydantic pydantic-settings sqlalchemy aiosqlite scikit-learn pyserial httpx pytest pytest-asyncio
}
Write-Host "Python dependencies verified." -ForegroundColor Green

# 3. Database Initialization & Seeding
Write-Host "[3/4] Initializing SQLite database and seeding demo fleet..." -ForegroundColor Yellow
python -m backend.app.db.init_db
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error initializing database!" -ForegroundColor Red
    exit 1
}
Write-Host "Database initialized and seeded." -ForegroundColor Green

# 4. Frontend Packages
Write-Host "[4/4] Installing React frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install --silent
Set-Location ..

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " BOOTSTRAP COMPLETE!" -ForegroundColor Green
Write-Host " To launch the platform, execute:" -ForegroundColor White
Write-Host "   .\scripts\start-dev.ps1" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Green
