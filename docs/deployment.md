# PRAHARI-NET Deployment Guide

## System Requirements
- **Operating System:** Windows 10/11, Linux (Debian/Ubuntu/Raspberry Pi OS)
- **Python:** Version 3.10+
- **Node.js:** Version 18+
- **Database:** SQLite with WAL mode (zero configuration required)
- **Hardware Interface:** Optional Silicon Labs CP2102 or CH340 USB-to-UART LoRa concentrator.

## Local Edge Launch Commands (Windows PowerShell)

```powershell
# 1. Start the complete system (Backend, Frontend, and Autonomous Simulator)
.\scripts\start-dev.ps1

# 2. Rebuild local Copilot BM25 RAG index
.\scripts\rebuild-copilot-index.ps1

# 3. Run Copilot unit and fast-path tests
.\scripts\test-copilot.ps1

# 4. Run Copilot load testing benchmark
.\scripts\benchmark-copilot.ps1

# 5. Stop running background services
.\scripts\stop-dev.ps1
```

## URLs
- **PRAHARI Command Centre Dashboard:** `http://localhost:5173`
- **FastAPI REST Endpoints & OpenAPI Docs:** `http://localhost:8000/api/docs`
- **WebSocket Real-Time Stream:** `ws://localhost:8000/ws/live`
- **Copilot Health Check:** `http://localhost:8000/api/copilot/health`
- **Copilot Metrics:** `http://localhost:8000/api/copilot/metrics`
