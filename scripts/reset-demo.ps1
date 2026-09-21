<#
.SYNOPSIS
  PRAHARI-NET Demo State Reset Script
.DESCRIPTION
  Resets simulator states, clears active test alerts, and re-seeds nominal baselines.
#>

Write-Host "Resetting PRAHARI-NET simulation & fleet state to nominal baseline..." -ForegroundColor Yellow

# Call simulator reset API if backend is running
try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/simulator/reset" -Method Post -TimeoutSec 3 -ErrorAction Stop
    Write-Host "Simulator reset via active backend: $($resp.status)" -ForegroundColor Green
} catch {
    Write-Host "Backend not running directly; re-initializing local SQLite database directly..." -ForegroundColor Yellow
    python -m backend.app.db.init_db
    Write-Host "Database clean nominal state seeded." -ForegroundColor Green
}
