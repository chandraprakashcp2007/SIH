# PRAHARI-NET Cinematic Frontend Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform every existing PRAHARI-NET frontend route into a cohesive cinematic emerald environmental-intelligence interface without changing production behavior or data truth.

**Architecture:** Migrate the existing React frontend in place around centralized Tailwind tokens, semantic CSS primitives, and a small set of reusable presentational components. Preserve current services, routing, state flows, and Leaflet implementations; route components adopt the shared system in dependency order.

**Tech Stack:** React 19, TypeScript, React Router, Tailwind CSS, CSS/SVG, Lucide React, Leaflet, Vitest, Testing Library, Playwright.

**Spec:** `docs/superpowers/specs/2026-09-28-prahari-cinematic-frontend-redesign.md`

## Global Constraints

- Do not change backend APIs, authentication contracts, WebSocket behavior, database contents, safety/provenance semantics, or node IDs.
- Do not use either supplied reference image or introduce a screenshot/poster-based UI.
- Keep Leaflet maps functional and interactive.
- Preserve exact project identity `PRAHARI-NET` and `पंजापुतम्`.
- Keep `REAL`, `SIMULATION`, `REPLAY`, `MODEL`, `EXTERNAL_DATA`, `NOT_CONFIGURED`, `BLOCKED`, `UNVERIFIED`, `METADATA_ONLY`, and `PLANNED` semantically distinct.
- Add no heavyweight visual dependency; use existing React, CSS, SVG, Lucide, and Leaflet.
- Respect `prefers-reduced-motion` and support keyboard navigation and mobile widths.
- Baseline database SHA-256: `D270B2882F3A8668081DC2498E3305E7F4255AAED8CA915D40D9560527223FE6`.

## Review Focus

- Production host with dev bypass disabled: login must never render credentials or demo shortcuts; covered by Task 3 tests.
- Missing, cached, or unverified data: UI must show an explicit source/empty state rather than operational certainty; covered by Tasks 1, 4, and 6 tests.
- Narrow viewport with sidebar, Copilot, and map controls: essential controls must remain reachable without page-level horizontal overflow; covered by Tasks 2, 4, and 7 tests.
- Reduced-motion users: continuous ambient, radar, and pulse animation must stop; covered by Task 1 CSS/test assertions.
- Existing Leaflet interactions and authenticated navigation: markers, selection, filters, protected routing, and logout must remain functional; covered by Tasks 2, 4, and 8.

---

### Task 1: Environmental Design Foundation

**Files:**
- Modify: `frontend/tailwind.config.js`
- Modify: `frontend/src/index.css`
- Modify: `frontend/src/prahari-premium.css`
- Create: `frontend/src/components/ui/CommandPrimitives.tsx`
- Create: `frontend/src/components/ui/CommandPrimitives.test.tsx`

**Interfaces:**
- Produces: `GlassPanel`, `SectionHeader`, `StatusBadge`, `SourceBadge`, `EmptyState`, and `MetricCard` React components plus semantic `.command-*` CSS classes and Tailwind color aliases.

- [ ] Write component tests asserting semantic headings, source labels, accessible status text, and empty-state actions.
- [ ] Run `npm test -- --run src/components/ui/CommandPrimitives.test.tsx`; expect failure because primitives do not exist.
- [ ] Implement the components, emerald token map, glass/depth utilities, environmental backgrounds, motion keyframes, focus rules, map styling, and reduced-motion overrides.
- [ ] Re-run the focused test; expect all assertions to pass.

### Task 2: Responsive Command Shell

**Files:**
- Modify: `frontend/src/components/layout/Layout.tsx`
- Modify: `frontend/src/components/layout/Navbar.tsx`
- Modify: `frontend/src/components/layout/Sidebar.tsx`
- Modify: `frontend/src/components/layout/Sidebar.test.tsx`

**Interfaces:**
- Consumes: Task 1 primitives/classes.
- Produces: grouped desktop navigation, mobile drawer, contextual header, operational/source state, and an accessible workspace frame.

- [ ] Extend shell tests for grouped labels, exact Hindi domain labels, mobile navigation controls, and logout accessibility.
- [ ] Run the focused layout tests; expect new assertions to fail.
- [ ] Implement the compact glass header, grouped sidebar, skip target, route-context title, responsive drawer, cached/offline banners, and collision-safe workspace.
- [ ] Re-run focused layout tests; expect pass.

### Task 3: Coded Cinematic Login

**Files:**
- Modify: `frontend/src/pages/Login.tsx`
- Modify: `frontend/src/pages/Login.test.tsx`

**Interfaces:**
- Consumes: existing authentication APIs and Task 1 styles.
- Produces: responsive coded CSS/SVG environmental scene and unchanged authentication behavior.

- [ ] Extend tests for exact identity, five node IDs, labeled fields, submit behavior, and absence of development shortcuts when backend/host conditions are false.
- [ ] Run the focused login test; expect new presentation assertions to fail.
- [ ] Implement the original SVG/CSS India network scene, domain cards, atmospheric layers, radar/cyclone motion, and frosted form while preserving auth logic.
- [ ] Re-run the login test; expect pass.

### Task 4: Command Centre and Leaflet System

**Files:**
- Modify: `frontend/src/pages/CommandCentre.tsx`
- Modify: `frontend/src/pages/MapPage.tsx`
- Modify: `frontend/src/components/map/LiveMap.tsx`
- Modify: `frontend/src/components/widgets/IncidentFeed.tsx`
- Modify: `frontend/src/components/widgets/PanchaBhoothaOverview.tsx`
- Modify: `frontend/src/components/widgets/LiveNodeStrips.tsx`
- Modify: `frontend/src/components/widgets/NodeDetailDrawer.tsx`
- Modify: `frontend/src/components/widgets/PanchaBhoothaOverview.test.tsx`

**Interfaces:**
- Consumes: existing summary/node/alert data and Tasks 1–2 layout contracts.
- Produces: truthful KPI composition, domain fabric, interactive emerald Leaflet map, incident rail, and responsive node intelligence.

- [ ] Add tests for source-mode labels, unavailable summary values, five domain IDs, and selection affordances.
- [ ] Run focused widget tests; expect new assertions to fail.
- [ ] Recompose Command Centre and map page with semantic primitives and retain filters, marker selection, popup, drawer, retry, and telemetry behavior.
- [ ] Restyle Leaflet markers, controls, popup, tooltip, legend, selected halo, and provenance overlays without changing tile or event logic.
- [ ] Re-run focused tests; expect pass.

### Task 5: Five Domain Experiences

**Files:**
- Modify: `frontend/src/pages/DomainIntelligencePage.tsx`
- Modify: `frontend/src/components/map/domains/NativeHazardMapBase.tsx`
- Modify: `frontend/src/components/map/domains/JalaFloodMap.tsx`
- Modify: `frontend/src/components/map/domains/AgniFireMap.tsx`
- Modify: `frontend/src/components/map/domains/BhumiLandslideMap.tsx`
- Modify: `frontend/src/components/map/domains/VayuAirMap.tsx`
- Modify: `frontend/src/components/map/domains/AkashaWeatherMap.tsx`
- Create: `frontend/src/pages/DomainIntelligencePage.test.tsx`

**Interfaces:**
- Consumes: existing domain API payloads and Task 1 primitives.
- Produces: one data architecture with five domain-specific visual modes and explicit evidence/provider limitations.

- [ ] Add route-context tests for exact Hindi/English identity, node IDs, provenance, unavailable layers, and prediction/provider abstention copy.
- [ ] Run the focused test; expect failure.
- [ ] Implement shared domain composition, environmental SVG/CSS motifs, telemetry/trend/evidence panels, and domain-specific map chrome.
- [ ] Re-run the focused test; expect pass.

### Task 6: Intelligence Routes

**Files:**
- Modify: `frontend/src/pages/AlertCentre.tsx`
- Modify: `frontend/src/pages/PredictionsPage.tsx`
- Modify: `frontend/src/pages/EvidenceGatePage.tsx`
- Modify: `frontend/src/pages/CrossHazardPage.tsx`
- Modify: `frontend/src/pages/AnalyticsPage.tsx`
- Modify: `frontend/src/pages/ReportsPage.tsx`
- Modify: `frontend/src/pages/DigitalTwinPage.tsx`
- Modify: `frontend/src/pages/ImpactIntelligencePage.tsx`
- Modify: `frontend/src/pages/AiIntelligencePage.tsx`
- Create: `frontend/src/pages/IntelligenceRoutes.test.tsx`

**Interfaces:**
- Consumes: existing route data fetches and shared primitives.
- Produces: alert triage, prediction uncertainty, evidence pipeline, linked-hazard graph, analytics, reports, twin/impact states, and premium Copilot surfaces.

- [ ] Add smoke/semantic tests for route headings, uncertainty/abstention, provenance, and missing-report states.
- [ ] Run focused tests; expect failure.
- [ ] Migrate each intelligence route to shared panels and its specified high-information layout without changing actions or API calls.
- [ ] Re-run focused tests; expect pass.

### Task 7: Assurance, Infrastructure, and Support Routes

**Files:**
- Modify: remaining files in `frontend/src/pages/*.tsx`
- Modify: `frontend/src/components/copilot/CopilotDrawer.tsx`
- Modify: `frontend/src/App.tsx` only if an existing capability requires a discoverable alias route.
- Create: `frontend/src/pages/SupportRoutes.test.tsx`

**Interfaces:**
- Consumes: existing service calls, Task 1 primitives, and Task 2 shell.
- Produces: visually consistent CAP, continuity, security, datasets, memory/events, simulator/lab, recovery/reports, network, health, readiness, calibration, logs, settings, external data, nodes, and demo routes.

- [ ] Add route smoke tests for headings, status/source labels, and nonblank unavailable states across the remaining page components.
- [ ] Run focused tests; expect failure.
- [ ] Migrate all remaining routes and Copilot to the centralized design system; expose existing memory/scenario/recovery capabilities through current routes or safe aliases without changing APIs.
- [ ] Re-run focused tests and the complete frontend unit suite; expect pass.

### Task 8: Responsive, Accessibility, Cleanup, and Full Verification

**Files:**
- Modify: `frontend/e2e/operations.spec.ts`
- Modify: frontend CSS/components where verification reveals defects.
- Modify: `docs/FINAL-READINESS-REPORT.md` only to record verified results.

**Interfaces:**
- Consumes: completed Tasks 1–7.
- Produces: verified production build, responsive behavior, accessible controls, database integrity evidence, and final commit.

- [ ] Extend Playwright coverage for login, authenticated navigation, five domains, Leaflet, representative desktop/mobile widths, production dev-shortcut absence, alerts, reports, and provenance.
- [ ] Run `python -m pytest -q -p no:cacheprovider`; expect full backend pass.
- [ ] Run `npm test -- --run` in `frontend`; expect full frontend pass.
- [ ] Run `npm run build` in `frontend`; expect TypeScript and Vite success.
- [ ] Run `npx playwright test` in `frontend`; expect all E2E tests to pass.
- [ ] Verify 1920×1080, 1366×768, 1024×768, Pixel 5, and small-mobile layouts; correct overlap, clipping, overflow, focus, or motion defects found.
- [ ] Run `git diff --check`; expect no whitespace errors and review every changed file.
- [ ] Recompute `data/prahari.db` SHA-256; require exact match with the baseline or stop without committing.
- [ ] Commit the complete verified change as `feat: transform PRAHARI into premium environmental intelligence UI`.
