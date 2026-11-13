# FAB.VISUAL Ω6B — Browser acceptance + recursive semantic refinement

Status: **experimental reference**, not a release. Base: draft PR #18 Ω6 painter parity. This is an additive patch; there is no mutation of live CodexStation hosts.

## Implemented

- `src/visual/semantic-refinement.mjs`: checks two distinct SceneIR views of a single model ID/revision; exhaustive unique child-to-parent part mapping; explicit numeric aggregation (`sum`, `mean`, `identity`), unit consistency, finite absolute tolerances, and fail-closed mismatch handling. Containment is a DAG; independent control/signal links can cycle. **No scientific validation.**
- `src/visual/semantic-drilldown.mjs`: two-level Anatomy SVG display with semantic part identity, evidence-panel readback, keyboard-operable controls and SVG semantics. Both the parent and child scene are explicitly analogical and synthetic.
- `examples/semantic-descent.mjs`: reproducible synthetic energy arithmetic example: 10 kWh + 14 kWh = 24 kWh. This is not a measured battery rack.
- `scripts/browser-qa.py`: Python Playwright drives locally generated HTML via `page.set_content`, since direct file and localhost navigation may be blocked. It checks keyboard/button navigation, state consistency, SVG naming, mobile viewport, reduced motion and no page errors; it captures full-page screenshots and JSON receipts.

## Reproduction

```bash
node --test tests/*.test.mjs
node bin/fab-visual.mjs anatomy-verify
node bin/fab-visual.mjs anatomy-timeline dist/anatomy-timeline.html
node examples/semantic-descent.mjs dist/semantic-descent.html
python3 scripts/browser-qa.py
```

Browser QA dependencies are optional and separate from the no-dependency Node reference runtime: `pip install playwright` and a locally available Chromium executable. It uses `--no-sandbox` because of the container; run **only generated, trusted in-memory markup**, without network or filesystem browsing, in an isolated disposable process. Never use this option for untrusted third-party pages.

## Evidence boundaries

Local Ω6B runtime: browser screenshots and receipt under `evidence/omega6-browser/`. Previous upstream Git blob pin remains unchanged. Full upstream original test suite, independent general geometry proof, multiple real browser engines, manual screen-reader testing, WCAG compliance and live CodexStation ABI: **NOT_RUN**. The CI workflow is a proposal until a real GitHub Action succeeds on this branch; do not infer CI PASS from local execution.

Release: **HOLD**, with no dedicated standalone GitHub repository created here.
