# Verification and claim ledger

## Implemented and locally tested (2026-11-13)

- SceneIR type validation, identity uniqueness, containment DAG, typed flows, port endpoint checks, nonfinite geometry rejection, numeric unit rule.
- Deterministic SVG rendering, XML escaping, accessible labels, static HTML view and model-derived readouts.
- Interactive timeline of precomputed synthetic states; avoids inventing intermediate model state.
- SHA-256 canonical model and output receipts (hashes attest bytes only; not correctness).
- Fail-closed release gate: synthetic example remains BLOCKED without evidence.
- Dry-run-only installer by default; opt-in copy, collision HOLD and no replacement.
- Reproduced source-equivalent adversarial counterexamples: nodal count threshold and same-theme publishing collision.

## Ω5 exact source subset + executed native geometry (2026-11-13)

- Verified five exact upstream Git blob hashes for Anatomy `kit/iso-kit.mjs`, `kit/lathe.mjs`, `kit/tube.mjs`, `kit/audit.mjs`, original MIT `LICENSE` at commit `1482e8469b0a9e0d8cc18ea2740a01423d29ae80`.
- Ran direct Node imports and upstream projection/solid functions, direct SDF checks and sampled depth ordering with its unmodified audit implementation.
- Implemented a separate deterministic isometric SVG renderer and 5-frame policy-state HTML timeline using original Anatomy geometry generation. The original Anatomy toolkit is separate from the older 2D reference renderer.
- Independent analytic AABB overlap detector and ray-box centerline occlusion oracle; these are bounded checks, not exhaustive computational geometry proofs.
- Reproduced thin-wire raster blind spot using actual upstream `A.overlapsOf` (wire radii 0.05 and 0.15: no detected pairs; 0.55: pair detected under our fixture).
- Added synthetic policy event-trace replay; forgeries of approval/readouts/part color and discontinuous timeline events are rejected. 54/54 local Node 22.16.0 tests pass.
- Static SVG raster inspection via CairoSVG succeeded; headless Chromium screenshot attempt did not complete. Browser interaction remains NOT_RUN/INCONCLUSIVE.

## Not yet verified

Full upstream Anatomy checkout/build/full audit, complete 3D and motion, isolated Chrome, cross-browser accessibility, scientific empirical validation, hardware claims, public GitHub dedicated repo creation, installed CodexStation release integration, production deployment or external certification.

## Mandatory release checks

SOURCE, MODEL, STATE, OBSERVABLES, GEOMETRY, SECURITY, ACCESSIBILITY, REPRODUCIBILITY, HOST_AUTHORIZATION, RIGHTS, CLAIM_BOUNDARY, PUBLICATION. Each check carries PASS / FAIL / NOT_RUN / INCONCLUSIVE / EXCEPTION, evidence digest, scope, covered states and test environment. An EXCEPTION is never a PASS. Product code may be tested while release remains BLOCKED.

## Ω6 candidate — bounded source audit closure (2026-11-13)
- Model replay check is now enforced in every **static** Anatomy SVG/HTML path when the model identifier is `fab.policy.reference`. The previous self-comparison of observables was tautological and was removed. Invalid/missing event traces block rendering, not merely the interactive timeline.
- Painter order is derived from `A.settle(...).items[*].key`, the same solved ordering that `A.depthOrder` evaluated, rather than recomputing unverified center-depth sorting. SVG carries explicit `data-paint-index` for testable output parity.
- Decorative link paths are explicitly `NOT_RUN` for geometry/depth audit and whole-scene assurance remains `INCONCLUSIVE`. A PASS describes bounded solid checks only.
- Root-level GitHub Actions now runs the actual nested product on push to the Ω6 branch and under the defined path-scoped pull-request trigger. A green first-party FDF workflow alone does not verify FAB.VISUAL.
- Claims remain restricted to a synthetic policy model. No physical metrology, browser accessibility, complete Anatomy upstream suite or production deployment is admitted.
