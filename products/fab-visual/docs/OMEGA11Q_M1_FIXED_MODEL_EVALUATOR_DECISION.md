# FAB.VISUAL Ω11Q-M1 — Fixed Synthetic Equation Evaluator (Research Candidate)

**Stage:** Ω11Q partial implementation (M1 only). **Release:** HOLD.
**Branch:** `feature/fab-visual-omega11q-m1-independent-evaluator`.
**Stacked base:** Ω11P draft PR #41 at `edaf1624f2d08bd62b7b238bb5c4d1bd4aff95dc`.
**Upstream:** pinned MIT Anatomy source `1482e8469b0a9e0d8cc18ea2740a01423d29ae80`, unchanged.
**Source:** first-party synthetic SceneIR `fab.visual.omega11l.energy` revision `0.6.0-alpha.0`.

## What actually executes

`src/visual/independent-model-evaluator.mjs` accepts only the exact typed synthetic model and fixed equation `SYNTHETIC_MICROGRID_BUS_BALANCE_V1`:

```
net_power_W = pv_W + battery_discharge_W - load_W - conversion_loss_W
net_energy_J = net_power_W * duration_s
```

The evaluator independently computes both outputs from explicit first-party synthetic inputs with whitelisted power/time units and compares computed values to separately declared expectations. It validates the canonical SHA-256 of the provided SceneIR, its model identity, revision and representation. No scene-provided code or plugin is executed. Known `site_export_power` source observable is a nonnumeric `NOT_CALCULATED` placeholder, so original-scene source-vs-rendered numeric readout remains `NOT_RUN` and must not be silently counted as a PASS.

## Initial synthetic test vector

PV 7 kW + battery discharge 3000 W − load 9 kW − conversion loss 1000 W = 0 W; over 3600 s gives 0 J. This is not a prediction of a real CitizenSolar site. Metamorphic checks include power scaling, load perturbation, duration scaling and explicit SI conversion; adversarial checks include digest/claim/model drift, forged authority fields, unsupported units, nonfinite inputs, negative uncertainty/invalid expected values, forbidden dynamic evaluators and source-readout discrepancies.

## Scope limitations

This work provides an independently executed *fixed reviewed arithmetic equation*. It does **not** establish an independently validated physical simulation, instrument provenance, metrology, source-defined physics, scientific correctness, runtime 3D Geometry, GPU-present completion, or a real visual numeric readout. Arithmetic is bounded binary64 and is NOT the M2 exact rational/decimal interval oracle. Model inputs are first-party synthetic declarations. The accepted v1 six-entry project ZIP, IDE installation controls, and upstream source bytes are unchanged.

## Proof obligations and admission gates

1. All inherited 273+ Node tests and M1 negative tests pass in independently checked Node 20 and Node 22.
2. All 173 original MIT Anatomy source objects and pinned vendored subset remain unchanged.
3. Existing three-domain Chromium offline Gallery and defended ZIP import/replay regressions pass.
4. CI exact HEAD, failure modes, hashes and output artifacts are independently inspected; do not infer results merely from a workflow declaration.
5. No source/readout numeric binding claim beyond what was actually verified. Production, physical, publisher signature, human/host authorization and publication remain `HOLD` / `NOT_RUN`.

## Successor

M2: construct independent exact decimal/rational interval arithmetic oracle with cross-checked rounding/cancellation, then M3 v2 source-bound quantitative sidecars, I1 actual versioned IDE compatibility, A1 real pinned Anatomy runtime/geometry checks. No automatic promotion to M2 or release without evidence.
