# FAB.VISUAL architecture (Ω4)

## Six planes

1. Evidence/source authority: source versions, empirical measurements, publication status, provenance.
2. Model semantics: typed SceneIR, state machines, units, source-linked observables, parent/child refinement.
3. Representation compiler: interprets PHYSICAL/ANALOGICAL/FORMAL and keeps stable IDs and geometry-independent semantics.
4. Specialized rendering: independent SVG reference renderer (implemented); Anatomy SVG/WebGL/3D adapter (plan only; not installed); optional CAD, VTK and Manim (candidate, not implemented).
5. Verification: model–visual correspondence, finite coverage, geometric checking, accessibility, security and reproducibility; negative results block admission.
6. Attestation and distribution: immutable evidence receipts, versioned code, skill and CodexStation opt-in extension; external authority admits releases.

## SceneIR v0.2

Required `schema`, `id`, `representation`, `model.id`, `model.revision`, `model.authority`, `parts`, `claim.status` and `claim.interpretation`. Each part has stable `id`, `label`, `x/y/w/h`, optional `parent`, and typed ports. Links have `from`, `to`, `flow`, optional verified port IDs. Domain observables have `id`, scalar or boolean/string `value`, `source` and explicit `unit` for numeric values. Containment must be a DAG; feedback flows may cycle. The reference renderer is a validated 2D SVG implementation; setting an isometric projection is illustrative and not equivalent to Anatomy's procedural solids.

## Correspondence contract

For every tested state `s` and declared observable `o`, renderer readout agrees with model evaluation within named tolerance `ε_o`: abs(R(s,o)-M(s,o)) <= ε_o for numbers, exact equality for booleans/strings. The full invariant is bounded to the actual tested state set unless formally proven.

## Portable host boundary

The CodexStation installer copies an additive skill and runtime into a new namespace. It never writes to `AGENTS.md`, station genesis, canonical memory, credentials, release policy, role registry or existing files. Installation is not authorization. Host release-specific integration review is mandatory.

## Threat boundaries

Untrusted model inputs, agent-authored code, generated HTML, headless browser tooling, WebGL shaders and third-party source are separate trust domains. Avoid running Anatomy Chrome helpers privileged or with broad filesystem/network access. Use isolated worker pools if browser checks are enabled.

## Known missing work

1. Actual upstream Anatomy kit checkout and build verification; 173 blob tree enumerated from GitHub only.
2. Full visual audit execution and cross-browser snapshots.
3. Arbitrary physical/engineering fidelity beyond synthetic example.
4. CAD/VTK/Manim adapters.
5. Formal refinement proofs, interval geometry oracle, deployment-signed witnesses, public security review.
