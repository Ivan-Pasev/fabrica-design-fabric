---
name: fab-visual
description: Build model-governed, evidence-carrying visual explanations and render synthetic interactive mechanisms. Use for model-to-SVG/HTML output, visual provenance, claim boundaries, and source-locked Anatomy planning. Never grant yourself host permissions.
---

# FAB.VISUAL (portable, model-agnostic)

Use this skill when the task needs a scientific, engineering or computational visual object with verifiable state or provenance.

## Process

1. Establish whether the representation is `PHYSICAL`, `ANALOGICAL` or `FORMAL`; record claim and source model.
2. Obtain verified domain inputs, units, state transitions and observable contracts; distinguish synthetic examples from claims about actual systems.
3. Validate `fab.scene.v0.2` via `bin/fab-visual.mjs validate`.
4. Render through the independent reference renderer (`render`) or produce an Anatomy adapter plan (`anatomy-plan`). Do not assume the latter is installed.
5. Compare all observable readouts with the authoritative model. Audit geometric sampling limitations separately.
6. Collect source hashes, test logs, render screenshots, accessibility, security and reproduction evidence.
7. Refuse to mark a released, certified, authorized or physically validated claim unless a separate responsible authority supplies the needed proof and release gate.

## Commands

From the source-repository root: `node bin/fab-visual.mjs demo dist/policy-machine.html`.
From an installed CodexStation root: `node .codexstation/extensions/fab-visual/bin/fab-visual.mjs demo dist/policy-machine.html`.
`node bin/fab-visual.mjs validate fixtures/policy-scene.json` (repository fixture only)
`node bin/fab-visual.mjs render fixtures/policy-scene.json dist/scene.svg`
`node bin/fab-visual.mjs anatomy-plan fixtures/policy-scene.json`
`node bin/fab-visual.mjs inspect-upstream vendor/anatomy`
`node --test tests/*.test.mjs`

## Integration boundaries

Root CodexStation constitution and release-specific agent policy remain authoritative; this skill carries no implicit permission to clone, execute shell commands, browse the network, mutate a repo or publish. External original Anatomy source remains MIT and separately attributed. Rendering may be performed in an isolated worker with restricted filesystem/network access, never privileged Chrome on untrusted input.

See `extensions/codexstation-fab-visual/AGENTS.md` and `docs/ARCHITECTURE.md`.
