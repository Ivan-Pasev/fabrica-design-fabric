# FAB.VISUAL Ω11D — Source-Defined Scene Stage Witness

Research date: 2026-11-14. Candidate source branch stacked on Ω11C PR #28.
Original pinned upstream remains wheresryan22/anatomy@1482e8469b0a9e0d8cc18ea2740a01423d29ae80 (MIT © 2026 Ryan; 173 tracked blobs). No upstream, main, CodexStation host, or production changes.

## New fault detected in prior Ω11C
For the Raptor-light hover witness, the previous generic CSS selector \`.iso-plate svg\` selected a 12×12 decorative icon within the figure rather than the full scene. It yielded a pointer at approximately (1078.5,86), and should never have been interpreted as a source-backed engine hover. The turning-light prior witness selected a 334×246 SVG with 760×560 viewBox. Even though eight fresh browser processes all completed and local three-frame screenshots were stable, both cases failed cross-process pixel-repeatability. The DOM census and hover hit alone were not a verified camera/frame identity.

## Surgical Ω11D correction
Apply source-derived stage selectors from immutable Anatomy generator source:
- Raptor stage: \`.rp-stage\` (accessible role slider with aria-valuenow/text) contains three SVG/canvas layers, not the plate PDF icon.
- Turning-dial stage: \`.ts-stage\` (accessible image) contains static/moving SVG layers.

A stage is admissible only when exactly one expected stage exists, its rectangle spans at least 120×100 CSS pixels, an actual descendant SVG has an independently observed client rectangle of at least 120×90 pixels and a four-value viewBox, and the center pointer hits a stage descendant or stage itself. This is a bounded *stage-target validity* predicate. It does not prove center pointer means a relevant anatomical part, correct camera state, or geometric visibility.

## Exact evidence to collect
The same two original source cases: raptor light at 1280px hover, turning light at 390px hover. Two fresh Chromium processes for each original/rebuilt side, three captured frames per process: 8 processes, 24 images, separate original and rebuilt pages. Preserve original HTML hashes, parsed model JSON hashes, Chromium version, toolchain, source lock, computed stage CSS opacity, transform/animation/transition, accessible role and value attributes, primary full-size scene SVG viewBox, stage rectangle and pointer/hit target, screenshots, and bounded classification.

Run the original source-specific numeric-drift diagnosis and all synthetic adversarial unit tests. Verify genuine stage capture in CI with exact reviewed source SHA and archive the receipt. An internally stable within-process screenshot cannot certify cross-process deterministic state. If a stage fails contract, classify explicitly and stop admission rather than fall back to a decorative SVG.

## Historical invariant ledger
Ω10B raw generated HTML byte parity: FAIL (3 original pages). Ω11B cross-run source-matched visual repeatability: FAIL. Ω11C historical archive forensics: PASS; Ω11C fresh-process execution: PASS; Ω11C same-source fresh-process pixel stability: FAIL on both affected scenes. Ω11C images showed 18 changed pixels pinned and 33 rebuilt in Raptor, and 121 pinned and 0 rebuilt in Turning. These observations are restricted to the previous *generic-icon* targeting algorithm and must not be treated as actual engine-stage observation.

## New admission gates
- Ω11D stage target source binding: PENDING exact CI.
- Ω11D independent 8-process/24-frame execution: PENDING exact CI.
- Source-backed camera/projection/frame identity: NOT_ADMITTED (unchanged).
- Independent 3D ray/mesh depth and occlusion: NOT_RUN (unchanged).
- HTML byte parity and prior cross-process reproducibility: FAIL (unchanged).
- Real host integration, accessibility certification, engineering metrology and scientific admission: NOT_RUN.
- Production release: HOLD.

## Next
Investigate actual CSS/browser frame nondeterminism using full scene only. Correlate source-embedded camera and mesh data to the captured scene through a new read-only adapter with explicit provenance and event/frame ID. For depth-order, use independently validated triangle/ray witnesses and geometry units. Do not infer mechanical clearance or scientific proof from screenshot appearance. No upstream source changes, privileges, or automatic merge.
