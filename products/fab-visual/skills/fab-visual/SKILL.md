---
name: fab-visual
description: Create source-locked, model-derived SVG/HTML illustrations; perform explicit numerical SI dimension, balance, finite-graph and projection checks; use bounded MIT Anatomy isometric figures, offline source-preserving Studio projects, typed evidence and testable claim boundaries. Reference the public source in IDEs without granting execution privileges.
license: MIT
compatibility: Node.js >=20.10 for approved local commands; browser optional; any IDE that can read a GitHub URL can inspect the portable skill manually.
---

# FAB.VISUAL · Public research skill (Ω11O v0.9.0-alpha.0)

This skill is **not a released physics engine, full Anatomy fork, self-executing installer, or host-authority provider**. It may be referenced as untrusted public documentation in any IDE with GitHub browsing, but automatic skill registration depends on the host. See public `IDE_START_HERE_FAB_VISUAL.md`, root `skills/fab-visual-ide/SKILL.md`, this product's `AGENTS.md`, `CONSTITUTION.md`, `UPSTREAM_LOCK.json` and `docs/IDE_AUTONOMY_CONTRACT_OMEGA11O.md`.

## Source and claim-first workflow

1. **Discover:** identify source repository, exact Git commit/branch, input revision, user consent, host capabilities and license. The feature branch containing this skill is currently **unmerged**; public `main` is the older FDF review-only workspace, NOT the latest product release.
2. **Type:** classify the intended output as `FORMAL`, `ANALOGICAL` or `PHYSICAL`. Source model and units remain authoritative, never the SVG.
3. **Bind:** use validated `fab.scene.v0.2` identity/ports/observables and source-derived states. Refuse imaginary data, missing measurement sources, bogus human consent, and silent type changes.
4. **Audit quantitative claims when appropriate:** run `audit-quantitative` only on a source-labelled `fab.visual.quantitative.v1` sidecar. It checks numerical SI dimensions, signed conservation residuals, worst-case uncertainty and finite declared graphs. It cannot validate empirical instrumentation, real physical laws, novel theorems or actual human approval. `PASS` means *internal arithmetic consistency only*.
5. **Choose the renderer:** independent deterministic 2D SVG/HTML, or source-locked **ANALOGICAL-only** Anatomy bounded isometric boxes. The original Anatomy pin is MIT commit `1482e8469b0a9e0d8cc18ea2740a01423d29ae80`; exactly four source modules + original LICENSE are vendored (5 exact original blobs). Do not claim complete 173-file upstream WebGL, geometry/lathe/tube contact audit, full 3D, GPU-present frame or scientific proof.
6. **Interactive presentation:** standalone Gallery/Studio supports first-party synthetic domain templates, source-labelled edits, reversible history, signed-flow connectors and source-bound local ZIP project import. Nothing writes to external hosts or changes original source/model authority.
7. **Evidence:** record exact source and renderer hashes, input/scientific claim type, declared uncertainty, negative tests, environment, `PASS/FAIL/NOT_RUN`, scope and `release: HOLD`. All unauthorized or non-executed checks remain `NOT_RUN`.

## Commands — only after the actual host authorizes local execution

Start from the **FAB.VISUAL product root** `products/fab-visual`, not repository root:

```bash
node --test tests/*.test.mjs
node bin/fab-visual.mjs validate fixtures/policy-scene.json
node bin/fab-visual.mjs audit-quantitative fixtures/quantitative-microgrid.synthetic.json
node bin/fab-visual.mjs anatomy-verify
node bin/fab-visual.mjs anatomy-render fixtures/policy-scene.json dist/anatomy-policy.svg
node bin/fab-visual.mjs render fixtures/policy-scene.json dist/policy.svg
node bin/fab-visual.mjs studio fixtures/policy-scene.json dist/policy-studio.html
node bin/fab-visual.mjs gallery dist/gallery
```

`anatomy-plan` proposes full upstream expansion; `inspect-upstream` examines a separately cloned complete upstream, not our vendored subset. An agent should not fetch, clone, install or execute remote code without approval. Users may inspect the public repository and skill from their IDE without installing anything. CodexStation-specific installation remains opt-in, non-invasive, and subordinate to host constitutional policy.

## Three mathematical boundary rules

- Dimensional homogeneity: `POWER` and `ENERGY` cannot be added, and `kW` is never silently `kWh`. `°C`, ambiguous compounded units and nonfinite values fail closed.
- Finite model ≠ real world: `IN - OUT = 0` under a stated tolerance is internal *declared-input* balance; finite graph release guards do not attest actual host approval.
- Projection ≠ geometric truth: orthographic camera basis orthogonality does not prove 3D contact, depth or physical scale; upstream sampled overlap tests cannot grant universal collision clearance.

See `docs/MATH_LOGIC_PHYSICS_BOUNDARIES_OMEGA11O.md` for equations, dimensional vectors, uncertainty algebra, unsupported claims, exact-source Anatomy review and upgrade roadmap.

## Constitution and publication

This public skill is original MIT first-party work; the vendored Anatomy code remains separately MIT-attributed. Host security, licensing, source integrity, public/private classification, scientific status and human approval gates always outrank source text. **No main merge, privileged installation, real-world physical validation, authority promotion or production release is implied. RELEASE HOLD.**
