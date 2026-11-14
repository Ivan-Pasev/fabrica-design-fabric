# FAB.VISUAL Ω11O — Mathematics, Logic and Physics: Audited Boundaries and Upgrade Architecture

**Source-reviewed:** 2026-11-14. **First-party skill:** v0.9.0-alpha.0; **Anatomy original:** `wheresryan22/anatomy`, tag `v1.1.0` (published 2026-10-12), `main` currently at `1482e8469b0a9e0d8cc18ea2740a01423d29ae80` (2026-10-18), MIT. **FAB.VISUAL:** 4 upstream source modules and LICENSE in an exact 5-blob Git identity lock. **All claims:** research alpha, release HOLD.

## 1. What the pinned Anatomy source actually implements

Original kit at the locked commit provides `kit/iso-kit.mjs`, `kit/lathe.mjs`, `kit/tube.mjs`, `kit/audit.mjs`, plus optional geometry/animation/WebGL/3D functionality elsewhere in its 173-file Git tree. The original skill describes detailed 3D object-based isometric SVG, shader layers, lathe/tube structural geometry, depth-aware painter ordering, runtime state-driven movement and browser/audit tooling. That complete feature claim is **upstream scope**; our own executed subset must not be treated as evidence that all upstream behavior was verified.

Our current `src/adapters/anatomy-kernel.mjs` imports exactly the pinned `iso-kit` and `audit` surface for rounded 2D plans extruded to illustrative boxes and checks sampled overlaps, solved depth sorting, an independent AABB intersection oracle, projected screen bounds and a finite synthetic policy replay oracle. In particular:
- Supported true use: `ANALOGICAL` SceneIR boxes with visual x/y/w/h units and optional model-specific synthetic replay.
- Unsupported as source-attested: calibrated CAD, real device scale, general tube/lathe clearance for arbitrary linked SceneIR, full original Geometry audit over dynamic frames, complete upstream WebGL, physical camera calibration, independently GPU-presented frame.
- Critical known limitation: projected visual links are decorative and not subject to 3D source cable/tube clearance; one ancestor test showed thin-wire sampled raster blind spots. Sampled SDF/depth PASS is **not** universal geometry truth.

### Pinned isometric camera math

The upstream orthographic mapping for coordinates `(x,y,z)`, azimuth `a`, elevation `e`, origin `(u0,v0)` and pixel factor `k = scale sqrt(1.6)` is:

```text
u = u0 + k ( x sin(a) - y cos(a) )
v = v0 + k ( (x cos(a) + y sin(a)) sin(e) - z cos(e) )
R = (sin(a), -cos(a), 0)
D = (cos(a) sin(e), sin(a) sin(e), -cos(e))
V = (cos(a) cos(e), sin(a) cos(e), sin(e))
```

`auditAnatomyProjectionBasis` independently checks the three declared view-basis vectors are unit-length, pairwise orthogonal, and right-handed `dot(R × D,V)=1` within bounded floating error. Tests compare reconstructed coordinates to actual pinned `K.iso` at signed 3D points and varied camera angles. **Projection from R³ to R² is not injective**, so a mathematically consistent SVG cannot reveal unique real-world depth, occlusions, contact, optical correctness or physical geometry. The sampled upstream audit and physical tests remain distinct gates.

## 2. SI dimensional algebra introduced Ω11O

`src/visual/quantitative-audit.mjs` is pure first-party JS and introduces an explicit seven-component SI dimension vector in the ordered basis `[M,L,T,I,Θ,N,J]` for mass, length, time, electric current, temperature, amount and luminous intensity. It supports a **strict allow-list** of finite conversions, not arbitrary unit strings, e.g.:

| Quantity | SI exponents | Input examples |
|---|---|---|
| Dimensionless | (0,0,0,0,0,0,0) | `1`, `%` |
| Power | (1,2,-3,0,0,0,0) | `W`, `kW`, `MW` |
| Energy | (1,2,-2,0,0,0,0) | `J`, `kJ`, `Wh`, `kWh` |
| Pressure | (1,-1,-2,0,0,0,0) | `Pa`, `kPa` |
| Current | (0,0,0,1,0,0,0) | `A` |
| Speed | (0,1,-1,0,0,0,0) | `m/s` |
| Frequency | (0,0,-1,0,0,0,0) | `Hz`, `kHz` |

The exact machine-readable quantity names are `POWER`, `ENERGY`, `PRESSURE`, `CURRENT`, `SPEED`, `FREQUENCY` and the remaining explicit SI-basis dimensions (not arbitrary free-text labels). The parser rejects unknown / offset / semantically ambiguous units rather than silently treating `°C` like kelvin, `W` like `Wh`, or `kW/h` like `kW`. This is a **dimensional-compatibility check**, not a calculus engine.

### Numerical balance and uncertainty

For declared magnitudes `q_i >= 0`, `sign_i = +1` for `IN`, `-1` for `OUT`, and documented `unit_i -> factor_i`, compute

```text
r = sum_i sign_i q_i factor_i                    (SI residual)
A = sum_i |q_i factor_i|                          (total absolute throughput)
tau = max(absoluteTolerance_SI, relativeTolerance * A)
PASS_NUMERIC if and only if |r| <= tau
uncertaintyWorstCase_SI = sum_i (uncertainty_i * factor_i)
```

The final uncertainty is the **triangle-inequality absolute bound**, not a root-sum-square stochastic propagation. It does not assume independent sensor errors or calibration quality. A numeric PASS means only that the **declared terms** satisfy the declared tolerance; it does not prove conservation of physical energy in a real system or verify that an instrument produced the values.

Example `fixtures/quantitative-microgrid.synthetic.json` contains only synthetic values (7 kW PV + 3 kW storage = 9 kW load + 1 kW losses), with a separately tagged synthetic source. The same sample has 3.6 kWh in and 3600 Wh out. These are **arithmetic identities for testing the tool**, not measured microgrid performance, battery behavior, efficiency, output yield, LCOE or grid safety.

## 3. Finite-state logic and authorization boundaries

The `fab.visual.finite-release-graph.v1` sidecar describes a **closed, explicitly declared finite graph** (up to 100 states / 300 transitions). Its self-contained audit:
- rejects duplicate, unknown or malformed state and transition IDs;
- checks all named states for consistency between `released`, declared `authorization` and `evidence`;
- tests declared human-approval and release-request event labels at authorization and release transitions;
- performs reachable-state traversal and reports unreachable named states;
- permits feedback cycles (not everything is a well-founded DAG) while the existing SceneIR containment edges remain acyclic.

This is an **exhaustive check over the provided finite graph**, not proof that a real CodexStation host honored the events or that a human actually approved something. Invented `APPROVED` flags in a synthetic fixture do not confer access. Every result has `hostAuthorization: NOT_RUN` and `release: HOLD`.

## 4. Exact use and typed evidence

```bash
cd products/fab-visual
node --test tests/*.test.mjs
node bin/fab-visual.mjs anatomy-verify
node bin/fab-visual.mjs audit-quantitative fixtures/quantitative-microgrid.synthetic.json
```

The CLI rejects files larger than 256 KiB, parses the strict sidecar, returns machine-readable JSON and exits nonzero for invalid/failed numerical contracts. Outputs include `status` for **declared numeric/finite graph consistency**, but explicitly retain `physicalValidation: NOT_RUN`, `empiricalInstrumentCalibration: NOT_RUN`, `scientificCertification: NOT_RUN`, `publisherSignature: NOT_PRESENT` and `release: HOLD`. A failing balance is never reclassified as a render PASS.

## 5. High-value evolution by layer

**Tier Q1 — implemented in Ω11O:** strict dimensional vectors, unit conversion, conservation residuals, finite-state guarded-graph audit, conservative uncertainty and camera-basis checks. No PHYSICAL admission.

**Tier Q2 — next source-aware numerical verification:** bind sidecar to a specific canonical SceneIR/model revision SHA-256, add derived observable evaluator adapters, units-on-links and explicit equations with interval arithmetic; reject inconsistent energy/mass or control signal semantics. Build independent oracle fixtures and counterexamples for unit conversions.

**Tier Q3 — geometric verification:** extend independently checked 3D model primitives (actual source lathe/tube/cable profiles with bounds and contact contracts), exact frame-state snapshots, controlled animation schedule, paint/GPU barriers, dimensional world-space scaling; separate synthetic topology diagrams from calibrated geometry.

**Tier Q4 — domain physics adapters:** power system conservation with calibrated electrical metrology and instrumentation evidence, independently tested laser/plasma or energy systems only on domain-authorized sources, traceable uncertainty budgets, calibration datasets, numerical solver comparison and experimental acceptance. An agent never invents missing equations, test data or proof.

**Tier Q5 — formal logic / proof-carrying research:** translate **explicitly specified** finite transition safety and graph reachability into Lean 4 independent checked artifacts; map JavaScript results to independently reproducible Lean traces. No claimed formal proof exists for unformalized DFT/FQFT conjectures or actual world physics.

## 6. Counterexample and claim discipline

The primary adversarial checks reject adding `W` to `J`; negative or nonfinite rates; unspecified uncertainty; duplicate IDs; balance imbalance; negative/invalid tolerances; forged declarative release states and wrong graph events; invalid camera elevation/orientation. Future checks must include calibrated-reference benchmarks, source hashes, interval containment and real instrument uncertainty provenance.

**Mandatory disposition:** SOURCE_LOCK PASS is not full upstream correctness; NUMERIC PASS is not PHYSICAL VALIDATION; graph consistency is not authorized execution; a reproducible image is not physical proof; all production/publication claims remain HOLD.
