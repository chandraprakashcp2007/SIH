<#
.SYNOPSIS
  PRAHARI-NET isolated regression suite.

.DESCRIPTION
  Runs backend, frontend, production build and Playwright without touching
  the normal development SQLite database.
#>

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " PRAHARI-NET ISOLATED REGRESSION SUITE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$testDb = Join-Path $root "data\prahari_test_isolated.db"

$previousDatabaseUrl = $env:DATABASE_URL

Remove-Item $testDb -Force -ErrorAction SilentlyContinue
Remove-Item "$testDb-shm" -Force -ErrorAction SilentlyContinue
Remove-Item "$testDb-wal" -Force -ErrorAction SilentlyContinue
Remove-Item "$testDb-journal" -Force -ErrorAction SilentlyContinue

$env:DATABASE_URL = "sqlite+aiosqlite:///./data/prahari_test_isolated.db"

$success = $true

try {

    Write-Host ""
    Write-Host "[1/4] BACKEND TESTS" -ForegroundColor Yellow

    & ".\.venv\Scripts\python.exe" -m pytest tests/ -q -p no:cacheprovider

    if ($LASTEXITCODE -ne 0) {
        throw "Backend tests failed."
    }

    Write-Host ""
    Write-Host "[2/4] FRONTEND UNIT TESTS" -ForegroundColor Yellow

    Set-Location (Join-Path $root "frontend")

    npm test

    if ($LASTEXITCODE -ne 0) {
        throw "Frontend tests failed."
    }

    Write-Host ""
    Write-Host "[3/4] TYPESCRIPT + PRODUCTION BUILD" -ForegroundColor Yellow

    npm run build

    if ($LASTEXITCODE -ne 0) {
        throw "Frontend production build failed."
    }

    Write-Host ""
    Write-Host "[4/4] PLAYWRIGHT DESKTOP + MOBILE" -ForegroundColor Yellow

    npm run test:e2e

    if ($LASTEXITCODE -ne 0) {
        throw "Playwright tests failed."
    }

}
catch {

    $success = $false
    Write-Host ""
    Write-Host "REGRESSION FAILURE:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red

}
finally {

    Set-Location $root

    if ($null -eq $previousDatabaseUrl) {
        Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
    }
    else {
        $env:DATABASE_URL = $previousDatabaseUrl
    }

    Remove-Item $testDb -Force -ErrorAction SilentlyContinue
    Remove-Item "$testDb-shm" -Force -ErrorAction SilentlyContinue
    Remove-Item "$testDb-wal" -Force -ErrorAction SilentlyContinue
    Remove-Item "$testDb-journal" -Force -ErrorAction SilentlyContinue
}

Write-Host ""

if ($success) {

    Write-Host "============================================================" -ForegroundColor Green
    Write-Host " ALL PRAHARI REGRESSION CHECKS PASSED" -ForegroundColor Green
    Write-Host " Development DB was not used by this runner." -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green

}
else {

    Write-Host "============================================================" -ForegroundColor Red
    Write-Host " TEST FAILURE - DO NOT COMMIT AS GREEN" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red

    throw "PRAHARI regression suite failed."
}
