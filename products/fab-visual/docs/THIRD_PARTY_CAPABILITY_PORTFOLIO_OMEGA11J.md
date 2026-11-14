# FAB.VISUAL Ω11J — High-value GitHub capability portfolio and lawful absorption map

**Date:** 2026-11-14 · **Scope:** actual product capabilities first; the central DB records evidence but is NOT the product. All external observations are source-referenced. Current integration is **format compatibility only**, except the already pinned vendored MIT Anatomy subset.

## Candidate sources, license evidence and absorption decisions

| Upstream | Reviewed ref / branch | License as inspected | Value | Current classification |
| --- | --- | --- | --- | --- |
| [Anatomy](https://github.com/wheresryan22/anatomy) | `1482e8469b0a9e0d8cc18ea2740a01423d29ae80` | MIT (copyright 2026 Ryan) | Source-authored procedural isometric geometry, shape depth/audit; source subset already vendored | **PINNED SOURCE SUBSET IMPLEMENTED**; full 173-blob upstream immutable checkout verified |
| [XYFlow / React Flow](https://github.com/xyflow/xyflow) | `1bc405cd113618c17fd181b931a9fe573bec9fee` (main) | MIT; copyright 2019–2025 webkid GmbH | Rich node editor, canvas controls, graph workflows | **DATA FORMAT ADAPTER IMPLEMENTED**; editor runtime NOT imported |
| [Cytoscape.js](https://github.com/cytoscape/cytoscape.js) | `b768734100fa49d24f5652361e4f2f3bdbcbce86` (unstable) | MIT-style source LICENSE; The Cytoscape Consortium | Graph analysis, traversals, network interaction, layouts | **DATA FORMAT ADAPTER IMPLEMENTED**; analysis library NOT imported |
| [Mermaid](https://github.com/mermaid-js/mermaid) | `2b1e7f66c2bafcfa2cf5cfe1fdf5db569d7ffddb` (develop) | MIT; copyright Knut Sveidqvist contributors | Text-to-diagram interchange, documentation, model flows | **TEXT FORMAT ADAPTER IMPLEMENTED**; Mermaid renderer NOT imported |
| [Excalidraw](https://github.com/excalidraw/excalidraw) | `01dc5ec62e54e2b7868b8a527a1d293d8e3cc516` (master) | MIT; copyright Excalidraw | Annotation, freehand storyboard, visual collaboration | **CANDIDATE** — no current JSON adapter or runtime import |
| [tldraw](https://github.com/tldraw/tldraw) | main at 2026-11-14 | Root LICENSE not retrieved; license terms NOT VERIFIED | Whiteboard, collaborative visual canvas | **HOLD** — do not copy/import or represent as permissively licensed without exact package-level checks |
| Graphviz DOT | Open graph description syntax, no upstream code imported | No upstream code used | Auditable graphs and publication pipeline | **ORIGINAL TEXT FORMAT ADAPTER IMPLEMENTED** |

Git commit SHA is the observed head at review time, not a guarantee that an uninstalled version is API-compatible. A MIT source license does not make a purported runtime integration real. Future imports require exact per-package SPDX/license/NOTICE, version pin, ABI test, security review and attribution. The existing Anatomy source is the only reviewed external code actually executed in the new Studio build (via the prior vendored subset).

## Product-facing roadmap ordered by immediate user value

1. **Ω11J implemented:** Validated SceneIR -> independent reference SVG and pinned Anatomy isometric -> interactive offline Studio (view switch, compare, inspect, search, flow filter, zoom) -> six user-triggered downloads including four interchange formats. No framework dependency.
2. **Ω11K candidate:** Import workflows from compatible XYFlow and Cytoscape serialized data into *typed* SceneIR. Preserve model authority and source/role metadata; reject unsupported node types, invalid coordinates, dangling edges and forged claims. Add round-trip loss ledger.
3. **Ω11L candidate:** Human-in-the-loop canvas editing with constrained move/resize/link operations. New scene revisions must have explicit source authority, not covertly mutate original snapshots or authorizations. Choose a safely pinned optional editor runtime only after licensing/ABI review.
4. **Ω11M candidate:** Responsive visualization packs for energy systems, research apparatus, agent orchestration, dependency graphs and multi-state evidence timelines. Source models validated separately; domain-specific numerical or physical outputs require independent evaluators.
5. **Ω11N candidate:** Real renderer and export compositor boundary (animation/GPU/frame status) only after actual source-glLayer call graph and controlled device/backend benchmarking. No green frame badge from screenshot or DOM alone.

## Constitutional acceptance and adverse cases

- Never turn a derived visual graph, Mermaid text, browser screenshot or source-input metadata into a theorem proof, physical metric or CodexStation execution permission.
- Reject unsafe SceneIR: duplicate part IDs, dangling endpoints, invalid flow/ports, nonfinite positions, unbounded layout payloads. Studio/format adapters each cap 300 parts, 800 links and 300 observables.
- Escape HTML and script JSON. Mermaid uses generated stable node IDs and sanitized labels; DOT uses quoted and HTML-encoded labels. Tests cover hostile strings, newlines, quotes and forged directives.
- Fully offline Studio: content security policy denies remote script/fetch and externals; browser import of upstream frameworks is not required. Local export is a deliberate user interaction.
- Each output emits canonical SHA-256 provenance, explicit model/claim status and **release HOLD**. Data transport compatibility alone does not certify downstream browser runtime compatibility.
- When adding external actual code: DISCOVER -> LICENSE -> SOURCE PIN -> ARCHITECTURAL MAP -> isolated optional import -> NOTICE/attribution -> build tests -> adversarial controls -> signed release decision. Do not conflate already-executing Anatomy source with unexplored future libraries.
