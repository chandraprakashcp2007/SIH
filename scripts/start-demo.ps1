<#
.SYNOPSIS
  PRAHARI-NET Instant SIH Jury Demo Launcher
.DESCRIPTION
  Launches stack and automatically opens the browser directly to the SIH Walkthrough route (/demo).
#>

Write-Host "Launching PRAHARI-NET SIH 2026 Jury Demo Flow..." -ForegroundColor Cyan

# 1. Start dev servers
& ".\scripts\start-dev.ps1"

# 2. Wait for startup
Start-Sleep -Seconds 2

# 3. Open default browser directly to /demo
Start-Process "http://localhost:5173/demo"
