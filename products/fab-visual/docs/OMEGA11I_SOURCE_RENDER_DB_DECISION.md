# FAB.VISUAL Ω11I — Source-renderer evidence and central SQLite v0.3

**Classification:** Research-only. Immutable source and bounded API-call audit. Real compositor/GPU present NOT_ADMITTED. Real geometry/depth NOT_RUN. Release HOLD.

## 1. Immutable provenance

Original upstream wheresryan22/anatomy at Git commit 1482e8469b0a9e0d8cc18ea2740a01423d29ae80, MIT Copyright (c) 2026 Ryan, 173 tracked Git objects verified independently, no original mutation. Research branch stacks on unmerged Ω11H PR #33. Source entry objects:

- examples/raptor-engine/live.js, blob c3c6a53d1f57f8e3743fb78dc391c251e19f6660
- examples/turning-dial/stress.mjs, blob 0dadd6e5584785e6678ec0a80f7a42be18b50c06

## 2. Pinned call-site audit (not complete JavaScript semantic proof)

Raptor live.js has 2 requestAnimationFrame call sites, 1 IntersectionObserver constructor, 3 setTimeout and 5 clearTimeout, 2 references to D.camera, a glLayer renderer and stage CSS transform. Its native timeouts are NOT controlled by the synthetic clock. Turning stress.mjs has 2 requestAnimationFrame call sites, 1 IntersectionObserver, 2 performance.now, 1 controller.set and 2 Date.now references in the generator source. Date.now is generator-time, not proof of browser runtime Date.now. Synthetic RAF/visibility/performance substitution intentionally changes browser semantics and cannot attest natural production behavior.

## 3. Test-only browser WebGL API witness

A separate pre-page test instrument intercepts HTMLCanvasElement.getContext and successful WebGL1/WebGL2 drawArrays and drawElements method calls. This does not change the exact original HTML bytes but DOES monkeypatch browser prototypes. A second independent exact-input synthetic RAF clock remains installed.

In CI #43580395260, 12 Chromium 143.0.7499.4 fresh browser processes executed (two scenes × original/minimal/observing × two). The full Raptor stage .rp-stage was 932×900 with two canvas and three SVG children. Every Raptor test process requested two WebGL contexts; Turning requested zero in these samples. The interception recorded zero wrapped drawArrays/drawElements calls across all 12 cases. This is only a bounded API observation: zero intercepted calls does NOT demonstrate lack of all possible drawing or GPU work, and no GPU-presented-frame claim is admitted.

One finite negative finding: Raptor full-observer screenshots differed across the two fresh processes despite identical stage outerHTML hashes; independent PNG comparison found six changed screenshot pixels. Raptor original/minimal and all Turning side pairs had equal screenshot SHA in that exact run. This is a FAIL of the narrow Raptor full-observer screenshot-repeatability predicate, not source-model numerical nondeterminism or physical inconsistency. The prior Ω11H synthetic-clock results used a different observer and cannot be silently generalized.

## 4. Central SQLite v0.3

The exact prior Ω11H v0.2 DB SHA is c54ee65951058f7ada58ce61e6cf3807f605620b244461808596677e6dce360e. This immutable file contains 37 earlier gates, 44 evidence references and eight real Ω11G checkpoint IDs. The reviewed native Sheet readback at modified time 2026-11-14T08:56:59.962Z contained 43 gates (23 PASS, 6 FAIL, 11 NOT_RUN, 1 HOLD, 2 INCONCLUSIVE) and 52 evidence references. Provider revision CAS token and human signature were not available.

The v0.3 compiler checks all 37 old gate values and all 44 evidence rows against the native source snapshot, then appends six gates and eight evidence references to a NEW database file; it retains all checkpoint IDs, CI lineage and original FAIL/HOLD restrictions. It refuses a changed baseline SHA, forged approval or provider revision, duplicate IDs and silent old-record changes. First independent verified artifact: CI #43580087229, then second source revision CI #43580395260 with browser instrumentation. Both reached valid SQLite integrity and source-lineage checks; second full run passed 48 adversarial Python tests and 12 browser cases. The v0.3 SQLite SHA in the first archived candidate and the runtime-probe source revision is 1a41f407a86eb573b0e2ea52e4023c376ce1859772dc465771eb14f0982c6522 (118,784 bytes). This is a frozen offline source projection; the native Sheet remains status authority. No managed server, automatic sync, production release or scientific admission was implemented.

## 5. Strict claim boundary

- SOURCE_PIN / CALLSITE_AUDIT: bounded source-verified.
- APPLICATION_UPDATE: source-applied ordinal after genuine callback, synthetic-clock-controlled test only.
- SOURCE_STAGE_DOM / SCREENSHOT: observed values; cannot certify GPU-present or zero perturbation.
- WEBGL_CALL_INTERCEPT: bounded API-call observation, not proof of GPU composition or presentation.
- GPU_PRESENTED_FRAME: NOT_ADMITTED without independent frame identity and authenticated compositor boundary.
- REAL_MESH_DEPTH: NOT_RUN without source-identified model geometry, camera, transforms, units and independent depth reference.
- Existing HTML byte parity and natural-source cross-process screenshot reproducibility FAIL remain. Production RELEASE HOLD.

## 6. Next gate Ω11J

Extend source-locked analysis into the actual glLayer implementation and browser draw/compositor barriers, compare natural timing against controlled timing, quantify observer-induced changes, and establish a signed/revision-aware database approval layer only when actual provider revision and human authorization become available. Avoid upgrading missing GPU/physical evidence by inference. Preserve original source and unmerged draft lineage.
