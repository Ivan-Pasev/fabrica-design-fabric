# FAB.VISUAL Ω9 — Model-backed semantic inspection and mobile magnification

**Status:** Research candidate; software and synthetic-browser admission only. Production, scientific validity, WCAG/screen-reader conformance, and authorization remain HOLD.

## Source and problem

Ω8 SVG output scales the 1200-unit technical figure into a 390px mobile viewport. The full diagram fits without horizontal document overflow, but SVG labels become impractically small. A zero-overflow assertion is not an accessibility or readability test. The two-level synthetic semantic refinement already exists, but neither the timeline nor the descent UI provides model-derived component controls with enlargement.

## Ω9 implementation

The shared `src/visual/semantic-inspector.mjs` presentation adapter is used by both:

- `src/adapters/anatomy-timeline.mjs` (5-frame synthetic policy machine).
- `src/visual/semantic-drilldown.mjs` (2-level synthetic energy illustration).

It projects part identities/labels/current statuses from each **validated source SceneIR** into accessible semantic HTML buttons. The selector never synthesizes status or changes the source model. For the registered policy reference model, model replay checks and existing release invariants remain required before image generation. The illustrative semantic energy model remains `model_evidence: NOT_RUN`, with a narrow numerical parent-child refinement check.

The UI supports four zoom presets (100, 150, 200, 300 percent), keyboard-operable zoom buttons, a named scrollable diagram region, a focusable component list, current-state status readout via `role=status`, synchronized selected-part highlight and local pan-to-selection. Model readouts remain separate from the illustrative SVG, and no changes are made to geometric audit criteria, body release gates or host permissions.

## Local executable evidence

- Node.js v22.16.0: original 91 regression tests plus 6 new inspector/model-binding tests = **97/97 PASS**.
- Local Chromium 144 via Playwright: six scenarios (390, 768, 1280 widths × 2 demos) totaling **118/118 PASS**, with 12 screenshots (zoomed and post-interaction for each scenario).
- Tests cover zoom and reset, >=44px zoom target height, >=16px inspect readout, document overflow isolation, keyboard controls, current part selection and diagram highlighting, release-state evolution after model replay, two-level semantic descent, reduced-motion preference and page JS exceptions.
- Source-level regression reproduces and blocks premature RELEASED state in model-controlled HTML. Component text uses `textContent`, and JSON embedded script data escapes `<` to avoid HTML injection.

All viewport and text tests are **bounded browser-computed assertions**, not optical or assistive-technology certifications. Browser is a disposable local Chromium environment rendering our own synthetic HTML only. Local root Chromium uses `--no-sandbox`; it must not be allowed to load untrusted documents.

## Scope and remaining gates

- Current semantic hierarchy depth remains **two levels only**. Component selection is not a generalized recursive knowledge explorer.
- The figure is a visual analogy. Part-position/zoom geometry is presentation only; it is not physical metrology.
- Real Android/iOS assistive tools, VoiceOver, TalkBack, keyboard-only usability with actual participants, contrast analysis and reader zoom up to 400% remain not tested.
- Full upstream Anatomy 173-blob acquisition, true 3D connector routing, rendering across browsers and any live CodexStation installation remain HOLD.
- Every release manifest must distinguish `MODEL_REPLAY_PASS`, `SEMANTIC_INSPECTOR_PASS`, `BROWSER_SMOKE_PASS` from `SCIENTIFIC_VALIDATION` and `RELEASE_APPROVED`.

## Next focused mutation

Conservative camera-space 3D connector tube/endpoint envelope verification and multi-browser real legibility assessments; do not promote 2D screen-space checks into a 3D clearance guarantee.
