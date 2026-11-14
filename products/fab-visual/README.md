# FAB.VISUAL

**Model-governed, evidence-carrying procedural visualization with a portable CodexStation extension.**

**Status:** `v0.4.0-alpha.0 / Ω11J` functionality candidate; independent Node/browser acceptance evidence archived per exact GitHub Actions head, **no production release**. FAB.VISUAL now includes a standalone offline Studio combining a reference SVG renderer and **actual pinned Anatomy isometric renderer**, plus dependency-free graph interoperability. The 173-file full upstream browser and 3D assurance suite is not reproduced by this product; no scientific certification is implied.

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
