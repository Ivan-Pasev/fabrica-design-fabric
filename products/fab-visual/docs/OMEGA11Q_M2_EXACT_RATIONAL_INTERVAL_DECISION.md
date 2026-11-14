# FAB.VISUAL Ω11Q-M2 — Decimal-Exact Rational Interval Research Candidate

**Status:** isolated, stacked draft research; **RELEASE HOLD**.  
**Source base:** Ω11Q-M1 PR #42 at `f934747cf4ab0d3fdcb5754dd9f1ef858ab931f3`.  
**Constitution:** source rights, model provenance and host authorization remain separate.

## Implemented fixed arithmetic

- `src/visual/exact-interval.mjs` parses **decimal text** (not binary64 JSON numbers) into reduced positive-denominator `BigInt` rational pairs, with coefficient, exponent, scale and intermediate-size limits.
- Only typed power (W/kW/MW), energy (J/Wh/kWh), time (s/ms/h) and dimensionless factors are accepted; offsets and implicit dimensional conversions fail closed.
- A first-party fixed synthetic microgrid equation creates conservative term-level closed intervals under arbitrary worst-case correlation (no stochastic independence assumptions). A positive duration multiplies the interval without reversed ordering.
- Exact absolute power tolerance and expected energy ± exact tolerance are separately compared with closed-interval `WITHIN_DECLARED_BOUNDS`, `OUTSIDE_DECLARED_BOUNDS`, `INCONCLUSIVE_OVERLAP`. Relative tolerance is intentionally not supported and cannot be silently inferred.
- Canonical original SceneIR SHA-256, model ID/revision, representation and synthetic attribution are checked before evaluation. A hash of a trusted supplied scene does not establish an external signature.
- The M2 synthetic case: (7,kW+3000,W-9,kW-1000,W = 0,W) nominal; declared worst-case uncertainty encloses ([-140,+140],W), hence **INCONCLUSIVE**, not physical PASS, at (1,W) tolerance. At (3600,s) the energy enclosure is ([-504000,+504000],J), also **INCONCLUSIVE**.

## Cross-language independence and test surface

A separate Python `decimal.Decimal` + `fractions.Fraction` oracle does not import the JavaScript rationals. Its normalized rational results are compared against Node `BigInt` across **10,000 deterministically seeded synthetic vectors**, each with mixed power units, signed contributions and positive durations. New Node adversarial tests cover exact 0.1+0.2, decimal/exponent equivalence, cancellation, closed interval endpoints, SI scaling, forged authority, source/model drift, invalid units, malformed decimal text, ambiguous float inputs and resource limits.

The CI workflow preserves the inherited Node suite, original 173 pinned Anatomy MIT Git objects, existing offline Gallery and defended six-member ZIP import/replay, and release gate HOLD. Both push and PR exact-HEAD, Node 20/22, Python reference evidence, the source lock and browser receipt must independently PASS before calling this research increment verified.

## Hard claim boundaries

This is mathematically **exact arithmetic on declared finite decimals**, not independently measured physical conservation, real-world uncertainty certification, a Lean proof, external publisher authentication, a rendered numeric readout check, a GPU-present frame, a CodexStation host install or a public v1 release. `NOT_RUN` and `HOLD` statuses are explicit. Historical Ω10B byte-parity FAIL, cross-process visual reproducibility FAIL and Ω11P binary64 interval INCONCLUSIVE remain unchanged.

**No existing CLI, project ZIP v1, upstream source, native Sheet gate, main branch, hardware or host authority is modified.**

## Successors

M3: separately admitted versioned science-evidence ZIP, preserving the strict six-member v1 opener.  
I1: actual isolated version-pinned IDE discovery and reference-only installation tests.  
A1: full Anatomy renderer/3D/GPU fidelity, independent physical/metrology programme.
