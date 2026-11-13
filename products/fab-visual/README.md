# FAB.VISUAL

**Model-governed, evidence-carrying procedural visualization with a portable CodexStation extension.**

**Status:** `v0.2.0-alpha.0` engineering reference; 32 local tests pass; **not released to production**. The independent renderer executes; the external Anatomy runtime is source-locked but **not included** and its complete upstream checkout is not locally reproduced. No scientific certification is implied.

## Architecture

```
Authorized domain model / evidence
         |   typed observables + unit conventions
         v
FAB SceneIR v0.2 (validate contract, containment DAG, typed flows)
         |                        |
         |                        +--> Anatomy adapter plan (HOLD until verified)
         v
Independent SVG / HTML reference renderer
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
node bin/fab-visual.mjs gate examples/codexstation-policy/manifest.json
```

The `demo` produces an independently generated HTML/SVG analogy of synthetic CodexStation authorization states. The generic renderer also emits a SHA-256 evidence receipt with `release: HOLD`.

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
License: MIT, copyright 2026 Ryan. No original source included. `node bin/fab-visual.mjs inspect-upstream vendor/anatomy` requires a separate exact, Git-backed checkout; missing and mismatched installations fail closed.

The existing independent SVG reference renderer **is not** the Anatomy geometry engine. For actual Anatomy rendering, its kit/graphics/audits must be installed, integrated and exercised with browser tests in a contained environment. See `docs/UPSTREAM_ABSORPTION.md` and `docs/VERIFICATION.md`.

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
| `src/adapters` | External, pinned Anatomy adapter plan and source inspection |
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

Canonical private research root: [FAB.VISUAL on Google Drive]([private canonical Drive source — supplied separately to authorized operators]).

Drive controls current research state, source/evidence ledger and official handoff. Public repository copies must be reviewed as public-safe derivatives, **not** unfiltered mirrors of private CodexStation contents. The future dedicated public repo target is `Ivan-Pasev/fab-visual`; do not treat this target as a live URL unless it has been created and verified.

## Security and contribution

See `SECURITY.md`, `CONTRIBUTING.md`, `AGENTS.md`, `CONSTITUTION.md`, `NOTICE`, `CHANGELOG.md` and `docs/VERIFICATION.md`. No credentials or actual internal CodexStation memory/state are shipped. Browser scripts from upstream must not run against untrusted pages in privileged environments.
