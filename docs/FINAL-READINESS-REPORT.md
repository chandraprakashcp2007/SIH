# PRAHARI-NET Final Readiness Report

Date: 2026-09-21

## Decision

**Ready for a local Smart India Hackathon demonstration.** The verified scope includes authentication/RBAC, authenticated real-time updates, simulator scenarios, risk/alert processing, readiness/calibration pages, reports, offline labeling, and PRAHARI Copilot. It is **not certified for unattended production emergency response** until real LoRa/serial hardware and deployment security are validated.

## Verification evidence

| Check | Result |
|---|---|
| Backend pytest | 68 passed |
| Frontend Vitest | 4 passed across 2 files |
| Playwright E2E | 4 passed: desktop and Pixel 5 profiles |
| TypeScript + Vite production build | Passed; 1,909 modules transformed |
| Main JS bundle | 240.91 kB raw / 77.58 kB gzip |
| Largest lazy chunk | Node detail/chart: 162.35 kB raw / 47.16 kB gzip |
| Telemetry load | 1,000/1,000 success; 0.00% errors; 40.1 packets/s |
| Telemetry latency | mean 24.11 ms; p50 20.87 ms; p95 45.80 ms; p99 85.72 ms; max 129.25 ms |
| Copilot load | 100/100 answered; 0.00% errors; 3.26 s total |
| Copilot latency | mean 305.69 ms; p50 93.98 ms; p95 1,777.75 ms; p99 3,152.20 ms |
| Protected API smoke | Unauthenticated system summary returned HTTP 401 |
| CSV smoke | Authenticated telemetry CSV returned HTTP 200 and `text/csv` |
| Scenario smoke | FLOOD_RAMP engaged and RESET completed |

Measurements are local-machine results, not capacity guarantees. The simulator was active during the ingestion benchmark, exercising concurrent background writes.

## Service status

- Auth: local bypass is enabled by `.env`, clearly labeled in the login UI, accepts any non-empty credentials, and maps reserved demo names to roles. Configuration defaults to safe disabled behavior when no local environment file is supplied. Database-backed password verification remains active when disabled.
- REST/RBAC: protected and role-gated as documented in the audit.
- WebSocket: authenticated with signed token transported as a negotiated subprotocol rather than a URL parameter; telemetry, risk, alert, trust, gateway, network and simulation events are available.
- Copilot: deterministic live-data paths, corrected entity/RAG behavior, Tanglish tolerance, sessions, SSE, sources, copy/stop/recent-chat/deep-link UI, and provider fallback are implemented.
- Offline/PWA: last-known core operational responses are cached and explicitly marked CACHED; browser offline is labeled LOCAL EDGE; stale values are not labeled LIVE.
- Hardware: serial bridge authentication and common ingestion path are complete; physical COM/LoRa verification remains pending.

## Commands

Bootstrap once:

```powershell
Set-Location C:\Users\GODWIN\Downloads\SIH
.\scripts\bootstrap.ps1
```

Start and stop:

```powershell
.\scripts\start-dev.ps1
.\scripts\stop-dev.ps1
```

Verify:

```powershell
.\scripts\run-tests.ps1
Set-Location frontend
npm run test:e2e
Set-Location ..
.\.venv\Scripts\python.exe scripts\stress-demo.py
.\.venv\Scripts\python.exe scripts\stress-copilot.py
```

Hardware gateway (after setting `SERIAL_PORT`, credentials, and `DEV_AUTH_BYPASS` appropriately):

```powershell
.\.venv\Scripts\python.exe gateway\serial_bridge.py
```

## URLs

- Frontend: http://localhost:5173
- SIH demo route: http://localhost:5173/demo
- Backend: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/api/docs
- WebSocket: ws://127.0.0.1:8000/ws/live (authenticated by the frontend)

## Final SIH demo procedure

1. Run `scripts\start-dev.ps1`, open the frontend, and point out the visible DEV AUTH BYPASS label.
2. Sign in as `admin` with any non-empty password. Explain that production uses normal database authentication when bypass is disabled.
3. Open **System Readiness** and confirm live gateway, database, nodes, risk, alert, PWA, Copilot and simulator checks.
4. Open **Command Centre** and show JALA-01, AGNI-02 and BHUMI-03 live telemetry plus WebSocket updates.
5. Open **Simulator**, engage **Flood Water Ramp**, and watch JALA risk/evidence evolve. Demonstrate alert acknowledgement with the operator/admin role.
6. Engage **False Smoke Sensor Spike** and explain cross-sensor trust suppression; then engage **Confirmed Fire**. With vision disabled, no camera confidence is fabricated.
7. Engage **Internet Severed (Local Edge)** and show the explicit LOCAL EDGE state while local telemetry/risk continues. Use browser offline mode to show cached data is labeled CACHED rather than LIVE.
8. Open PRAHARI Copilot. Ask `jala status`, `gateway okay ah`, and `alert ethavathu iruka`; show sources, timestamps, streaming, copy and deep links. Ask `status of JALA-99` and confirm the explicit not-found response.
9. Open **Calibration** to show admin-only persisted settings, then **Reports** to download telemetry/alerts/events CSV and open incident evidence.
10. Return to **Simulator**, run **Recovery**, then **Reset**. Confirm readiness and the command centre return to the nominal baseline.

## Production gates

Before any real deployment: set `DEV_AUTH_BYPASS=false`; rotate `SECRET_KEY`; restrict `CORS_ORIGINS`; enable TLS; provision the gateway account; validate the physical serial/LoRa path; define backups/retention; and perform domain-authority calibration of thresholds and response procedures.
