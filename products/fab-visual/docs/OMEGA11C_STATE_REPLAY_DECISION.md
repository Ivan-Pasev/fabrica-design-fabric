# FAB.VISUAL Ω11C — Source-Locked Cross-Run Forensics and Fresh-Process State Witness

Date: 2026-11-14. Status: independently executable *research candidate*, never a release.
Source lineage: Ω10B PR #25 → Ω11A PR #26 → Ω11B PR #27 → current Ω11C stacked draft.
Immutable upstream: \`wheresryan22/anatomy@1482e8469b0a9e0d8cc18ea2740a01423d29ae80\`, MIT © 2026 Ryan, 173 blobs.

## 1. Evidence-conservation premise

Ω10B: ORIGINAL_SOURCE_LOCK=PASS, BOUNDED_NUMERIC_DRIFT=PASS, GENERATED_BYTE_PARITY=FAIL (three HTML files).
Ω11A: idealized static segment-to-AABB synthetic oracle PASS; not a physical/mesh proof.
Ω11B: 18/18 Chromium original/rebuilt finite observations executed on same source commit; first run 16 equal / 2 pixel deltas, second run 18 equal / 0 pixel deltas. The 18-pixel Raptor-light and 121-pixel turning-light discrepancies are *not reproducible across those successful runs*. This invalidates any unsupported claim that source numerical drift caused those observed pixel changes.
No prior FAIL is repaired or erased.

## 2. New independent forensic auditor

\`scripts/omega11c-crossrun-audit.py\` takes two archived GitHub Actions evidence ZIPs and fails closed on mismatched upstream source hashes, browser/Playwright/configuration, missing/duplicate cases, source pin mismatch, incomplete execution, release-boundary tampering or screenshot SHA mismatch. It compares first-run and second-run original and rebuilt images independently, giving changed-pixel counts, maximum RGBA channel variation, affected bounding boxes, case classification mismatches and source provenance. It creates a *separate opaque-red inspection overlay* rather than relying on potentially transparent RGBA differences. Archive re-packing by CI does **not** change individual screenshot bytes; only the repacked ZIP hash changes.

Expected archive-specific bounded observations: 18 cases, two classification mismatches, 18 RGB-level pixels in the rebuilt Raptor-light 1280px hover image, 121 in the original turning-light 390px hover image; the corresponding other-side captures are identical across runs. Source numeric causation remains NOT_ESTABLISHED.

## 3. Fresh process replay

\`scripts/omega11c-state-replay.py\` checks original HTML SHA256 (known committed file), requires a single source-embedded JSON constant (\`const D = …\` or \`const DATA = …\`), records its canonical model-data digest and read-only camera fields where present. It captures two cases, each with 2 browser processes per original/rebuilt side, 3 frames per browser process. Recorded browser values include hovered element, pointer position, SVG bounding rectangle and viewbox, visible SVG/path census, readouts, browser version, runtime errors and network attempts.

A successful replay **does not** imply actual camera-state equivalence. The on-page model may not expose a unique render frame/camera event ID. \`true_camera_frame_state=NOT_ADMITTED\` is a permanent result for this increment, even when pixel repeatability happens to PASS. Missing or different readback is recorded as failure or inconclusive rather than invented semantic identity.

## 4. CI and adversarial tests

Independent CI: \`.github/workflows/fab-visual-omega11c.yml\`, read-only repository and Actions permissions, immutable upstream checkout and source hash lock, complete three-source original rebuild, original narrow drift diagnosis, standalone Pillow unit/adversarial tests, two historic artifact downloads into disposable evidence, and Chromium/Playwright fresh-process replays. It records exact job HEAD, Node/V8/Python/OS versions, hashed outputs and two evidence artifacts.

Test contract includes original SHA rejection, missing embedded model, page/frame state mismatch, within-process jitter, between-process pixel drift, blocked external resources, missing process, transparent-alpha difference issue, screenshot-hash forgery, source/provenance mismatch and malicious ZIP traversal.

## 5. Claim ledger

| Predicate | Initial candidate status |
|---|---|
| Original upstream 173-blob source lock | Inherited PASS; recheck in exact new CI |
| Historical two-archive forensic comparison | PENDING exact CI |
| Fresh Chromium-process replay execution | PENDING exact CI |
| Cross-run pixel stability of prior Ω11B evidence | FAIL |
| Strict original/rebuilt generated HTML byte parity | FAIL |
| Source-bound unique camera/frame state readback | NOT_ADMITTED |
| Real model-backed camera movement/occlusion/mesh clearance | NOT_RUN |
| macOS/Linux low-level numeric-drift causation | NOT_RUN |
| Real host installation / screen reader / scientific validation | NOT_RUN |
| Production release | HOLD |

## 6. Next bounded gates

G11C3: independently connect real model-space camera pose/projection and animated frame event ID to each browser capture, or retain NOT_ADMITTED. Implement verified moving ray/depth order and occlusion controls for the known normal seam and float drift, not generic SVG opacity. Validate cross-process source-backed state signatures.
G11C4: repeat pinned upstream Node/V8 generators on both macOS and Ubuntu with instruction-level provenance and immutable original outputs; attempt source-causal diagnosis without global numerical rounding.
G11C5: cross-browser/assistive technology, true world-space mesh/swept-port geometry and sanitized exact host ABI review require separate evidence/authorization. No PR auto-merge, no host mutations or scientific claims.

Release stays HOLD unless each independent hard gate is explicitly closed.
