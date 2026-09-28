# PRAHARI-NET Cinematic Frontend Redesign

**Date:** 2026-09-28
**Scope:** Existing frontend only; production behavior and contracts remain authoritative.

## Objective

Transform the complete PRAHARI-NET interface into a cohesive, premium environmental-intelligence command platform. The visual system must communicate spatial awareness, operational seriousness, evidence integrity, and the five Pancha Bhootha domains without becoming a decorative mock-up or making unsupported operational claims.

The two supplied images establish a quality bar for composition, density, lighting, glass depth, map prominence, and environmental color language. They are not implementation assets. No pixels, tracing, screenshots, poster layers, or pre-rendered interfaces from those references may enter the product.

## Invariants

- Preserve all backend routes, payloads, authentication behavior, WebSocket behavior, database contents, source/provenance semantics, safety rules, report/export behavior, and existing Leaflet functionality.
- Retain existing frontend URLs and working interactions. Additional navigation entries may expose already implemented backend capabilities, but no backend contract will be changed for presentation purposes.
- Preserve PRAHARI-NET, `पंजापुतम्`, and node IDs `JALA-01`, `AGNI-02`, `BHUMI-03`, `VAYU-04`, and `AKASHA-05` exactly.
- Distinguish `REAL`, `SIMULATION`, `REPLAY`, `MODEL`, `EXTERNAL_DATA`, and unavailable states. Visual polish must never imply a connected provider, validated sensor, or operational capability that the data does not support.
- Keep maps interactive and DOM-based. Use CSS, SVG, existing icons, gradients, and lightweight animation rather than large visual assets or a 3D rendering dependency.

## Visual System

### Foundation

The base palette is near-black teal and deep emerald (`#020B0B`, `#051F20`, `#0B2B26`, `#163832`, `#235347`) with mint text and interaction accents (`#8EB69B`, `#DAF1DE`). Surface hierarchy is created through translucency, narrow luminous borders, low-opacity radial light, subtle grid/contour texture, and restrained shadows rather than opaque black cards.

Domain accents remain subordinate to the green identity:

- JALA: aqua/cyan
- AGNI: amber/orange
- BHUMI: olive/earth
- VAYU: mint/turquoise
- AKASHA: sky-cyan/subtle violet

Typography uses Inter-compatible system sans for interface text and JetBrains Mono-compatible monospace for telemetry, IDs, timestamps, and provenance. Devanagari receives sufficient line height and font fallback support.

### Depth and Motion

Surfaces use three reusable depth levels: inset telemetry surfaces, standard glass panels, and elevated command overlays. Motion is limited to transform and opacity where possible: ambient light drift, radar sweeps, marker/status pulses, chart reveals, environmental flow, hover elevation, and drawer transitions. All essential information remains static and legible with `prefers-reduced-motion`.

### Reusable Primitives

The migration introduces shared semantic classes/components for glass panels, metric cards, section headings, source/provenance badges, risk/status badges, empty/loading/error states, tab systems, map frames, compact data rows, and environmental ambient layers. Existing components adopt these primitives incrementally so the frontend is evolved rather than replaced.

## Application Shell

The authenticated shell uses a compact fixed glass header, grouped collapsible sidebar, responsive mobile drawer, and layered workspace background. The header presents contextual route identity, local/system mode, connectivity, source state, alerts, user role, and sign-out without crowding smaller viewports. Navigation groups are Operations, Pancha Bhootha, Intelligence, Assurance, and system/demo utilities.

The shell owns consistent page spacing, route entrance treatment, offline/cached banners, skip/focus behavior, and mobile overlay management. It must not duplicate navigation or allow overlay collision with the persistent Copilot.

## Login Experience

The login is a real two-column interface. Its cinematic scene is constructed from gradients, CSS atmosphere, an original SVG India/network visualization, radar rings, telemetry points, a scanning orbital beam, storm/cyclone motifs, and five domain markers. The authentication form continues to call the existing auth service and retains production-safe behavior. Development shortcuts render only when the backend explicitly enables bypass and the host is local.

On narrow screens the narrative scene compresses above the form without hiding authentication or creating fixed-width overflow.

## Command Centre and Maps

Command Centre becomes the primary operational composition: truthful KPI strip, five-domain fabric, dominant interactive map, active incident feed, and live node intelligence. Existing backend values remain the only source for counters and status. Unknown values use evidence-aware empty states.

Leaflet tiles, controls, markers, popups, selection, filtering, and events remain functional. Styling adds emerald tile treatment, domain markers, selected halos, active-risk pulses, glass legends, provenance/source badges, and responsive control placement. No satellite, radar, terrain, or provider layer is visually claimed unless supplied by the application.

## Domain Intelligence

The shared domain architecture keeps one data flow and five visual modes:

- JALA emphasizes river flow, level/rate trends, thresholds, and flood evidence.
- AGNI emphasizes thermal pulse, smoke/gas telemetry, anomaly corroboration, and vision availability.
- BHUMI emphasizes contour depth, slope, saturation, tilt, vibration, and terrain-source limitations.
- VAYU emphasizes atmospheric flow, gas/air measurements with correct sensor provenance, and plume uncertainty.
- AKASHA emphasizes radar-like atmospheric motion, rainfall/pressure trends, linked hazards, and external-provider availability.

Prediction and layer panels abstain visibly when evidence is insufficient. Decorative domain effects never masquerade as measured data.

## Intelligence and Assurance Routes

All existing routes inherit the new shell and primitives, then receive route-specific hierarchy:

- Alerts: filter/list/detail intelligence layout with accessible severity hierarchy.
- Predictions: source, confidence, uncertainty, trajectory, contributing evidence, and abstention.
- Evidence Gate: raw evidence → validation → trust → corroboration → decision pipeline.
- Cross-Hazard: evidence-backed relationship graph with provenance and confidence limitations.
- Analytics and reports: consistent dark charts/tables, premium tooltips, and nonblank missing-report states.
- Digital Twin and impact: current state, blind spots, uncertainty, unavailable feeds, and simulation separation.
- CAP, continuity, security, readiness, calibration, device health, logs, settings, datasets, network, external data, memory, scenario, recovery, demo, and Copilot: serious operational panels with truthful states and consistent interaction design.

Existing combined routes may continue to host related capabilities where splitting would alter established behavior. Navigation labels must make their contents discoverable.

## Responsive and Accessible Behavior

Layouts use fluid `clamp()`, `minmax()`, wrapping grids, and breakpoint-specific composition at 1920×1080, 1600×900, 1440×900, 1366×768, 1280×720, 1024×768, Pixel 5, and small mobile widths. Dense desktop canvases become ordered single-column or horizontal-scroll-safe data regions on mobile; essential content is never simply hidden.

All controls receive semantic labels, visible mint focus states, keyboard access, adequate contrast, and useful status text independent of color. Drawers and overlays retain accessible close controls and predictable focus order. Motion reduction disables ambient and continuous animation.

## Performance and Failure States

No new heavyweight visual dependency is required. CSS/SVG effects are capped or disabled on small screens, blur radii remain restrained, and existing lazy routes remain intact. Every data-bearing region supports loading, offline, no-data, not-configured, permission-denied, session-expired, withheld, and retry states as applicable.

## Verification

Before product edits, record the branch, commit, worktree state, and SHA-256 of `data/prahari.db`. After implementation:

1. Run backend tests with `python -m pytest -q -p no:cacheprovider`.
2. Run frontend tests with `npm test -- --run`.
3. Run the production build with `npm run build`.
4. Run Playwright with `npx playwright test`.
5. Run `git diff --check` and review all changed files.
6. Compare the database SHA-256 to the recorded baseline.
7. Verify production auth, all five domain routes, Leaflet rendering/interactions, and representative desktop/mobile layouts.

Tests will be updated only for intentional presentation changes, never weakened. Database mutation or an unexplained hash change is a stop condition. A commit is created only after the full transformation and verification are complete.
