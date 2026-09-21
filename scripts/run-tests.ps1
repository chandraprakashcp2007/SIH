<#
.SYNOPSIS
  PRAHARI-NET Automated Test Suite Runner
.DESCRIPTION
  Runs backend tests, frontend unit tests, production build, and optional browser E2E.
#>

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Running PRAHARI-NET Test Suite" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Backend Pytest
Write-Host "[1/3] Executing Python AI, Security & Ingestion Tests..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -m pytest tests/ -q -p no:cacheprovider
$backendExit = $LASTEXITCODE

# 2. Frontend tests
Write-Host "[2/3] Executing Frontend Unit Tests..." -ForegroundColor Yellow
Set-Location frontend
npm test -- --run
$frontendTestExit = $LASTEXITCODE

# 3. Frontend Typecheck & Build
Write-Host "[3/3] Executing Frontend TypeScript Validation..." -ForegroundColor Yellow
npm run build
$frontendExit = $LASTEXITCODE
Set-Location ..

Write-Host ""
if ($backendExit -eq 0 -and $frontendTestExit -eq 0 -and $frontendExit -eq 0) {
    Write-Host "ALL BACKEND AND FRONTEND TESTS PASSED SUCCESSFULLY!" -ForegroundColor Green
} else {
    Write-Host "SOME TESTS REPORTED FAILURES. Check logs above." -ForegroundColor Red
}
