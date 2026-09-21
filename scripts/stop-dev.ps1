<#
.SYNOPSIS
  PRAHARI-NET Process Shutdown Script for Windows
.DESCRIPTION
  Gracefully terminates backend uvicorn and frontend vite development servers.
#>

Write-Host "Stopping PRAHARI-NET local servers..." -ForegroundColor Yellow

# Kill uvicorn/python backend processes listening on port 8000
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.MainWindowTitle -like "*uvicorn*" -or $_.CommandLine -like "*backend.app.main*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

# Kill node/vite processes
Get-Process node -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*vite*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

# Fallback port release check
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Stop-Process -Id $port8000.OwningProcess -Force -ErrorAction SilentlyContinue
}
$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if ($port5173) {
    Stop-Process -Id $port5173.OwningProcess -Force -ErrorAction SilentlyContinue
}

Write-Host "PRAHARI-NET stack stopped cleanly." -ForegroundColor Green
