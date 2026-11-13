# Verification and claim ledger

## Implemented and locally tested (2026-11-13)

- SceneIR type validation, identity uniqueness, containment DAG, typed flows, port endpoint checks, nonfinite geometry rejection, numeric unit rule.
- Deterministic SVG rendering, XML escaping, accessible labels, static HTML view and model-derived readouts.
- Interactive timeline of precomputed synthetic states; avoids inventing intermediate model state.
- SHA-256 canonical model and output receipts (hashes attest bytes only; not correctness).
- Fail-closed release gate: synthetic example remains BLOCKED without evidence.
- Dry-run-only installer by default; opt-in copy, collision HOLD and no replacement.
- Reproduced source-equivalent adversarial counterexamples: nodal count threshold and same-theme publishing collision.

## Not yet verified

Upstream Anatomy checkout/build/audit, full geometry and motion, isolated Chrome, cross-browser accessibility, scientific empirical validation, hardware claims, public GitHub dedicated repo creation, installed CodexStation release integration, production deployment or external certification.

## Mandatory release checks

SOURCE, MODEL, STATE, OBSERVABLES, GEOMETRY, SECURITY, ACCESSIBILITY, REPRODUCIBILITY, HOST_AUTHORIZATION, RIGHTS, CLAIM_BOUNDARY, PUBLICATION. Each check carries PASS / FAIL / NOT_RUN / INCONCLUSIVE / EXCEPTION, evidence digest, scope, covered states and test environment. An EXCEPTION is never a PASS. Product code may be tested while release remains BLOCKED.
