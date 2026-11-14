# FAB.VISUAL Ω11J — Product Studio, Source-safe Interchange and Offline End-to-End Evidence

**Product version:** 0.4.0-alpha.0 · **Status:** ACTUAL FUNCTIONALITY TESTED / PRODUCTION RELEASE HOLD · **Base ancestry:** Ω11I unmerged draft PR #34, Git HEAD 97c9f1532973c15211bc944db7ec541f2ec92c5c.

## Working product capability

The research product now compiles valid SceneIR into a **self-contained HTML workbench**. A user can open the resulting HTML locally, change between an independent 2D SVG reference and the actual pinned Anatomy isometric projection when permitted, compare both, inspect named components and their recorded source statuses, search by label/ID, zoom, and toggle flow types. An offline download panel exports the original SceneIR JSON, SVG, XYFlow/React Flow nodes/edges JSON, Cytoscape.js graph JSON, Mermaid and Graphviz DOT.

This is **not a static screenshot**. The UI has real event listeners and each export produces downloaded bytes without server calls, as demonstrated in isolated Chromium. The Anatomy isometric view is source-locked to the five already vendored MIT Anatomy files, with its existing independent AABB and bounded depth constraints. Unsupported PHYSICAL/FORMAL scenes retain the 2D reference without fake geometry support.

## How to run

From products/fab-visual:

- node bin/fab-visual.mjs studio fixtures/policy-scene.json dist/fab-visual-studio.html
- node bin/fab-visual.mjs interchange fixtures/policy-scene.json reactflow dist/scene.reactflow.json
- node bin/fab-visual.mjs interchange fixtures/policy-scene.json cytoscape dist/scene.cytoscape.json
- node bin/fab-visual.mjs interchange fixtures/policy-scene.json mermaid dist/scene.mmd
- node bin/fab-visual.mjs interchange fixtures/policy-scene.json dot dist/scene.dot
- node --test tests/*.test.mjs

Every CLI generation emits an adjacent .witness.json with canonical model and artifact SHA-256 and release HOLD. All four graph exporters are independent schema/text projections, not copied editor runtime code; exact package version round-trip tests are a separate later obligation.

## Actual architecture

SceneIR v0.2 validator -> source-bound claims and typed topology -> reference SVG + optional audited pinned Anatomy isometric -> standalone HTML Studio -> semantic inspector + filter and compare -> local user-generated downloads. The format adapters accept only validated SceneIR and cap overly large graphs; arbitrary library source is not injected into the browser. The HTML page enforces a no-network CSP; source model values cannot be directly inserted as HTML script.

The product release gate remains external and intentionally unchanged. Model-derived graphics or payloads do not independently establish proof, scientific device measurements, physical clearance, real frame presentation, or host authorization.

## Evidence, provenance, and risk boundaries

First complete candidate CI #43587191055 on source HEAD 07c4d304b19ab9dfe31129d1ddcd12c1a0cdb959 passed **118 of 118 Node regression tests**, independent original Anatomy 173 blob source lock, CLI build of the standalone Studio and all four graph formats, and isolated Playwright Chromium 143 browser smoke cases. The browser verified real component search and selection (status=BLOCKED), 2D/Anatomy/compare display, downloadable SVG, SceneIR, XYFlow, Cytoscape, Mermaid and DOT, local no-network behavior and explicit release HOLD. The product artifact contains Studio HTML, graph files, three browser screenshots and SHA256SUMS. A later synchronized compare-zoom change and documentation edits require a new exact-head CI before accepting them as finally verified.

Known limitations: The Studio is a locally compiled static model view, not a browser-based arbitrary SceneIR editor or a live CodexStation host integration. The graph format adapters are projections; optional downstream runtime compatibility is not end-to-end verified. Isometric geometry remains analogical unless separately validated by model sources. Real 3D mesh/metrology, GPU-present frame attestation and scientific claims remain unadmitted or NOT_RUN. No existing FAIL/HOLD from Ω11I is promoted.

## Next prioritized product work (not database-dominant)

Round-trip import of XYFlow/Cytoscape into bounded SceneIR with explicit source model and loss ledger; in-browser scene editing and reversible version snapshots; reusable domain scene examples with explicit real source data; optional pin+license-checked collaborative editor integration; public-safe deployment only after release governance. The central SQLite database tracks event provenance and gate drift, not the primary product feature surface.
