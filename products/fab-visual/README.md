# FAB.VISUAL

**Model-governed, evidence-carrying procedural visualization with a portable CodexStation extension.**

**Status:** `v0.9.0-alpha.0 / Ω11O` product-capability research candidate, **not production-released**. FAB.VISUAL provides a standalone offline Studio, source-aware XYFlow/Cytoscape graph round trips, reversible local visual editing, evidence-carrying output witnesses, reference SVG and pinned MIT Anatomy isometric rendering for eligible unmodified analogical scenes. Actual model authority, host authorization, full upstream rendering, real GPU-presented-frame and physical/scientific validation remain outside this bounded product implementation.

## Ω11O — portable IDE skill + exact quantitative boundaries

**One-link IDE discovery:** paste `https://github.com/Ivan-Pasev/fabrica-design-fabric/blob/feature/fab-visual-omega11o-ide-science-skill/IDE_START_HERE_FAB_VISUAL.md` into a GitHub/HTTPS-capable IDE agent. The public `main` branch contains the earlier review-only bootstrap; this source is an **unmerged research branch**, not an automatically installed or released skill. See `skills/fab-visual-ide/SKILL.md`, `AGENTS.md` and `docs/IDE_AUTONOMY_CONTRACT_OMEGA11O.md`. Agent read-only analysis may be automatic when the host supports it; cloning, code execution, host writes and deployment require separate permission.

**Mathematics/logic/physics:** source-labelled quantitative sidecar verifies strict SI units and dimensional vectors, power/energy balance residuals, triangle-inequality uncertainty bounds and finite declared authorization-graph consistency. An independent test checks pinned Anatomy camera basis and source coordinate projection. All are bounded numeric or finite declarative results, not measured physics or actual human authorization.

```bash
cd products/fab-visual
node bin/fab-visual.mjs audit-quantitative fixtures/quantitative-microgrid.synthetic.json
node --test tests/*.test.mjs
```

All illustrative microgrid numbers are synthetic. `physicalValidation`, `scientificCertification`, `hostAuthorization` remain `NOT_RUN`; `release` remains `HOLD`. For equations, source analysis and negative fixtures see `docs/MATH_LOGIC_PHYSICS_BOUNDARIES_OMEGA11O.md`.

## Architecture

```
Authorized domain model / evidence
         |   typed observables + unit conventions
         v
FAB SceneIR v0.2 (validate contract, containment DAG, typed flows)
         |                        |
         |                        +--> Exact pinned Anatomy subset (MIT) / 3D isometric analogy
         v
Independent SVG/HTML + real Anatomy geometry rendering
         |
         v
Canonical SHA-256 output witness + adversarial tests
         |
         v
External authorization / publication gate (default HOLD)
```

Scientific/mathematical sources retain authority over facts. CodexStation deployments retain authority over identity, permissions, memory and public/private disclosure. This repository provides *visualization capability*, not those authorities.

## Quick start

Requires Node.js 20.10+; no runtime dependencies.

```bash
node --test tests/*.test.mjs
node bin/fab-visual.mjs demo dist/policy.html
node bin/fab-visual.mjs validate fixtures/policy-scene.json
node bin/fab-visual.mjs render fixtures/policy-scene.json dist/policy.svg
node bin/fab-visual.mjs anatomy-plan fixtures/policy-scene.json
node bin/fab-visual.mjs anatomy-verify
node bin/fab-visual.mjs anatomy-render fixtures/policy-scene.json dist/anatomy-policy.svg
node bin/fab-visual.mjs anatomy-timeline dist/anatomy-timeline.html
node bin/fab-visual.mjs gate examples/codexstation-policy/manifest.json
```

The `demo` produces an independently generated HTML/SVG analogy of synthetic CodexStation authorization states. The generic renderer also emits a SHA-256 evidence receipt with `release: HOLD`.

## New in Ω11J — usable offline Studio and interoperable graph exports

Create a self-contained visual workbench from **any valid SceneIR**. The Studio is a product UI: locally inspect real source-defined components, search by component label or ID, filter flow types, zoom diagrams, switch between the reference 2D and source-pinned Anatomy isometric views when eligible, compare their renderings, and download source/graph outputs without a web connection.

```bash
cd products/fab-visual
node bin/fab-visual.mjs studio fixtures/policy-scene.json dist/fab-visual-studio.html
# Open dist/fab-visual-studio.html locally in your browser.

node bin/fab-visual.mjs interchange fixtures/policy-scene.json reactflow dist/scene.reactflow.json
node bin/fab-visual.mjs interchange fixtures/policy-scene.json cytoscape dist/scene.cytoscape.json
node bin/fab-visual.mjs interchange fixtures/policy-scene.json mermaid dist/scene.mmd
node bin/fab-visual.mjs interchange fixtures/policy-scene.json dot dist/scene.dot
```

The Studio uses validated `fab.scene.v0.2`, no external runtime dependencies, and a restrictive no-network page policy. Its six local download options are SVG, original SceneIR JSON, XYFlow JSON, Cytoscape JSON, Mermaid, and Graphviz DOT. The scene hash and output hash are recorded in adjacent witness files. Graph adapters are original independent format projections, **not copied source code or runtime integrations** from XYFlow/Cytoscape/Mermaid. Format consumers still require compatibility checks against their actual installed versions.

The Anatomy view is available only for eligible `ANALOGICAL` scenes that pass the current bounded sampled/isometric source-audit. `FORMAL` and `PHYSICAL` scenes retain a safe 2D model-derived view and do not gain a 3D scientific or physical certification. Studio, graph data and downloaded scenes cannot authorize real CodexStation actions or change the release HOLD. See `docs/OMEGA11J_PRODUCT_STUDIO_DECISION.md` and `docs/THIRD_PARTY_CAPABILITY_PORTFOLIO_OMEGA11J.md`.

## Ω11N — reopen and replay your actual portable visual project

From the offline Gallery, open one of the three source-labelled domain Studios. In **Open portable project ZIP**, choose a `.zip` previously exported from the **same original Studio scene**.

On a successful import, the Studio checks the six-file ZIP structure and CRC32 without decompressing, the exact original source SceneIR against its locally compiled anchor, canonical SHA-256 via the browser Web Crypto API, fork ID/revision ancestry, every history snapshot and the current visual diff. It independently regenerates all six project files and requires byte-exact agreement. Without cryptographic hashing support or on any mismatch, import is rejected rather than silently trusted.

After verification, use the **local revision cards** and Previous/Next controls to preview a historical version in the two-panel visual diff. Press **Apply selected revision** to activate it locally; undo/redo and subsequent visual edits remain available. Rejected wrong-template ZIPs, corrupt entries, false release/approval metadata and stale source digests retain the existing editable scene. All import data is rendered as text/model structure rather than evaluated as script; no network request or host command is executed.

The importer is intentionally strict: only the exact six-entry uncompressed Ω11M **ZIP STORE** layout is accepted. Third-party ZIP utilities may rewrite entry metadata and are not guaranteed to pass; export directly from the Studio or `fab-visual project` CLI. ZIP CRC32 detects accidental damage, not malicious publishers. An exact source SHA-256 match proves byte-content correspondence with the currently opened Studio scene, not publisher authentication or model legitimacy.

### Local workflow

1. Open `dist/gallery/index.html`, then an editable Studio.
2. Change an illustrative layout and click **Download project ZIP**.
3. Reload that same Studio; choose the ZIP under **Open portable project ZIP**.
4. Select a revision card, inspect the source-versus-revision diff, and apply it locally.

Implementation: `src/visual/project-import.mjs`, `src/visual/editor-runtime.mjs` and `src/visual/studio.mjs`. Adversarial tests: `tests/project-import.test.mjs`. Real browser acceptance: `scripts/project-import-browser-smoke.py`. Domain projects remain synthetic/illustrative. Real hardware performance, scientific proof, independent GPU-presented frame, external publisher signature, actual host authorization and public release remain NOT_RUN / NOT_ADMITTED / HOLD.

## Ω11M — local visual forks, actual revision diffs and portable ZIP projects

From the generated offline Gallery, open any domain Studio and use Fork SceneIR, Compare source / current, the revision selector, Connect nodes on canvas, and Download project ZIP. This is functional local model-derived visualization, not an authorized model editor or a connected service.

**Fork:** supply a lowercase slug such as `research-01`. The exported `--fork-research-01` SceneIR has a distinct visual revision and an explicit source ID, revision and SHA-256 ancestry record. Original source model authority, claims and observables stay unchanged. Publisher signature status remains NOT_PRESENT.

**Visual diff:** switch between actual source-versus-revision 2D diagrams; inspect changed positions and sizes and typed links added/removed. These are illustrative canvas coordinates rather than metrology. Source-audited Anatomy isometric and comparison remain disabled after a visual edit until recompiled.

**Canvas connectors:** use pointer or Enter/Space on accessible source-defined SVG nodes and flow paths. Connector mode admits only compatible source port-flow categories; removing links and other edits remain undoable. No host authorization or empirical data is modified.

**Portable project:** the offline ZIP contains `manifest.json`, `source/original.scene.json`, `derived/fork.scene.json`, `evidence/visual-diff.json`, `evidence/edit-history.json`, and `readme.txt`. ZIP CRC32 is only a transport-integrity check, NOT a publisher signature. To inspect a project, unzip it locally; the Studio does not yet import whole ZIP archives as trusted projects.

```bash
cd products/fab-visual
node bin/fab-visual.mjs gallery dist/gallery
node bin/fab-visual.mjs project templates/energy-microgrid.scene.json templates/energy-microgrid.scene.json research-01 dist/energy-project.zip
```

The CLI also emits `dist/energy-project.zip.witness.json` with a SHA-256 checksum. Only canonical valid source SceneIR and visual-only derivatives may be packed. Invalid scene authority changes, malformed slugs, path traversal, unsafe link types, and forged scientific/approval fields are rejected by contract tests.

Implementation: `src/visual/project.mjs`, `src/visual/editor-runtime.mjs`. Tests: `tests/project.test.mjs`, `scripts/project-browser-smoke.py`. The original pinned MIT Anatomy source stays unchanged; no new external runtime, DB migration, live host installation, scientific or physical certification or production release. Release HOLD.

## Ω11L — three practical domain systems in a portable offline gallery

Run one command from `products/fab-visual`:

```bash
node bin/fab-visual.mjs gallery dist/gallery
# Open dist/gallery/index.html directly in your browser.
```

Output: one searchable, filterable offline `index.html`, three editable Studio HTML files in `studios/`, their original SceneIR JSON in `scenes/`, three SVG previews in `previews/`, and a SHA-256-linked `gallery.manifest.json`. All these files work together when the generated folder is kept intact. The gallery is not a single self-contained HTML file; the individual three Studios are each standalone.

The gallery has three FIRST_PARTY_SYNTHETIC domain templates:

- **Citizen Solar microgrid:** PV, battery, DC bus, inverter, load and dispatch, with typed energy, information and control links. Energy yield, site grid export and storage state of charge are NOT_CALCULATED / NOT_MEASURED.
- **GILC laboratory DAQ:** sample, chamber, pressure transducer, optical detector, DAQ, vacuum pump and interlock with typed material, signal and control connections. Pressure, exposure, metrology calibration and equipment safety are NOT_MEASURED / NOT_ASSESSED / NOT_RUN.
- **CodexStation evidence/approval:** synthetic request, planner, research, independent verifier, policy, human approval and blocked execution. There is no live connected agent or authorization; execution remains BLOCKED.

Every scene carries a source-label and explicit units for numeric observables; all empirical status is NOT_RUN. The gallery is a capability demonstration, NOT a measured engineering system, installed apparatus, scientific paper, operational agent authorization or external connected service. The templates are original first-party source and do not copy new external renderer/editor runtimes.

Open a domain's editable Studio from the gallery; move or resize components, add or remove typed illustrative links, undo/redo, download explicit local edit-history JSON, and export edited SceneIR / SVG / XYFlow / Cytoscape. Editing disables stale original Anatomy 3D/compare visualizations until recompilation and audit. No hidden server, DB migration, external network request or public deployment is involved. Scientific validation and production release remain **HOLD**.

The Gallery's source contract is `src/visual/gallery.mjs`, source models live in `templates/*.scene.json`, automated negative tests in `tests/gallery-templates.test.mjs`, and browser end-to-end verification in `scripts/gallery-browser-smoke.py`.

## Ω11K — source-anchored graph import and reversible local editing

Open the generated Studio locally and use **Offline visual editor** to move or resize source-defined components, create illustrative typed connections, undo/redo up to 32 local edits, and import exported XYFlow or Cytoscape JSON. The Studio can download the **edited** SceneIR, 2D SVG, XYFlow and Cytoscape projections; Mermaid/DOT are intentionally blocked after an edit to avoid offering stale original outputs. Recompile edited SceneIR through the CLI to regenerate those two graph formats. The original source file is not overwritten.

For portable CLI imports, the source SceneIR is required as an explicit authority anchor:

```bash
node bin/fab-visual.mjs studio fixtures/policy-scene.json dist/fab-visual-studio.html
node bin/fab-visual.mjs interchange fixtures/policy-scene.json reactflow dist/scene.reactflow.json
node bin/fab-visual.mjs interchange-import reactflow dist/scene.reactflow.json fixtures/policy-scene.json dist/roundtrip.scene.json
node bin/fab-visual.mjs interchange fixtures/policy-scene.json cytoscape dist/scene.cytoscape.json
node bin/fab-visual.mjs interchange-import cytoscape dist/scene.cytoscape.json fixtures/policy-scene.json dist/cytoscape.roundtrip.scene.json
```

Each import checks the versioned interchange envelope, source SHA-256 digest, model identity/revision/authority, original observables and claim, source component identities, stable hierarchy/status, typed ports, finite geometry, endpoints and flow types. A changed graph produces a derivative with `visualEdit` provenance plus `.import-report.json` and `.witness.json`. A matching `source_digest` is **self-reported correspondence**, not a cryptographically authenticated external publisher signature. Arbitrary unversioned third-party editor JSON is currently **rejected** rather than silently elevated to trusted SceneIR. XYFlow and Cytoscape editor runtime round-trip ABI verification remains a separate test obligation.

**Critical renderer boundary:** after any local visual edit, the Studio deliberately disables the original Anatomy isometric and compare views because their geometry would be stale. The edited reference 2D drawing is model-derived presentation only. Recompile from edited SceneIR to attempt bounded Anatomy audit; never assume real 3D part clearance, physics, formal proof or actual authorization. The current implementation is offline; there is no shared collaboration session, persistent service or automatic Google Drive / central DB sync.

See `docs/OMEGA11K_EDITABLE_STUDIO_DECISION.md` and `tests/graph-import.test.mjs` for formalized acceptance and adverse cases.

## Interactive timeline

For scripted demonstrations, import `interactiveTimeline` from `src/visual/interactive.mjs` and pass two or more valid SceneIR states. The control shows the *actual precomputed state snapshots*, not an invented animation or live CodexStation authorization.

## CodexStation installation — default dry run

```bash
node scripts/install-codexstation.mjs --root /path/to/codexstation
node scripts/install-codexstation.mjs --root /path/to/codexstation --apply
```

Creates an additive skill under `.agents/skills/fab-visual` and an extension under `.codexstation/extensions/fab-visual`. Refuses collisions; cannot replace a host constitution, alter network access, enable browser scripts, grant permissions, or release anything. The installed package is `INSTALLED_NOT_AUTHORIZED` until host-specific review.

## External Anatomy source

Source: https://github.com/wheresryan22/anatomy
Reviewed pin: `1482e8469b0a9e0d8cc18ea2740a01423d29ae80`.
License: MIT, copyright 2026 Ryan. A narrow exact-source subset is now included under `vendor/anatomy/` with original upstream LICENSE and SHA-pinned `SOURCE_LOCK.json`. Run `node bin/fab-visual.mjs anatomy-verify` to verify all five original blobs. `inspect-upstream` remains exclusively for a *separately obtained complete Git-backed checkout* and is not appropriate to the partial vendored subset.

The independent SVG reference renderer **is not** the Anatomy geometry engine. Ω5 adds a separate **actual Anatomy-based renderer**, using original `slabOf` and `audit` source, bounded sampled depth checks, independent AABB collision checking and replay-verified policy timelines. This is **not** proof of full upstream audit, all rendering modes or browser accessibility. For the full Anatomy suite, an isolated upstream checkout and browser/3D tests are still required. See `docs/UPSTREAM_ABSORPTION.md` and `docs/VERIFICATION.md`.

## Product boundaries

- `PHYSICAL`: engineering interpretation; claims require model validation and standards evidence.
- `ANALOGICAL`: explanatory mechanism; cannot certify the represented scientific or computational system.
- `FORMAL`: model/theorem representation; cannot assert a proof solely from a visualization.
- Containment must be acyclic; causal feedback/control flows can be cyclic.
- Explicit source, model revision, observable units, claim status and evidence required.
- `PASS` means a bounded test passed, not that a mathematical theorem or physical device is certified.

## Repository structure

| Path | Purpose |
|---|---|
| `src/visual` | SceneIR, model consistency, SVG/HTML, interactive timeline, provenance |
| `src/adapters` | Exact pinned Anatomy isometric renderer, independent AABB oracle, policy replay checker and upstream discovery |
| `vendor/anatomy` | Source-lock verified four original Anatomy modules and verbatim upstream MIT LICENSE |
| `src/gate.mjs` | Fail-closed publication admission |
| `bin/` | Zero-dependency CLI |
| `contracts/` | Machine-readable visual artifact schema |
| `skills/fab-visual/` | Portable Agent Skill |
| `extensions/codexstation-fab-visual/` | CodexStation constitutional overlay instructions |
| `scripts/` | Explicit opt-in installation and source-acquisition tooling |
| `fixtures/`, `examples/` | Synthetic examples, never host-authorized actions |
| `tests/` | Automated regressions and adversarial fixtures |
| `docs/` | Product specification, integration matrix, threat model, verification |

## Continuity / provenance

Canonical private research root: [FAB.VISUAL on Google Drive](https://drive.google.com/drive/folders/PRIVATE_CANONICAL_ROOT_REDACTED).

Drive controls current research state, source/evidence ledger and official handoff. Public repository copies must be reviewed as public-safe derivatives, **not** unfiltered mirrors of private CodexStation contents. The future dedicated public repo target is `Ivan-Pasev/fab-visual`; do not treat this target as a live URL unless it has been created and verified.

## Security and contribution

See `SECURITY.md`, `CONTRIBUTING.md`, `AGENTS.md`, `CONSTITUTION.md`, `NOTICE`, `CHANGELOG.md` and `docs/VERIFICATION.md`. No credentials or actual internal CodexStation memory/state are shipped. Browser scripts from upstream must not run against untrusted pages in privileged environments.
