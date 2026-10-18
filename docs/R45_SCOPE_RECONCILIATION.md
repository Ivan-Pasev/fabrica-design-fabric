# R45 — UI-only source scope reconciliation on EK-003 review stack

**Maturity:** draft review; first-party scope checker, not an IDE permission system. **No release, auto-install, caller edit, merge or deployment.**

## Pinned lineage
- Prior EK-003 draft PR #9 review head: `8ce147522ed1d14f67d8c8267c0d5ccb10fbf8b6`.
- Original R42 host operator file Git blob: `e0b711434dbeded3b4b21a3e08b4c10edfcf9c54`; identical in PR #9 before R45.
- R44 local package contained an applicable reviewer patch with five focused tests, but had not been committed to GitHub.
- R45 corrects the operator advisory on a **new branch stacked on PR #9**, leaving existing EK upstream reference-only registry/skills and EK-003 browser evidence intact.

## R45-F01 boundary
R42 permitted a syntactically accepted `CONTINUE()` intent scoped to non-UI paths to receive `HOST_CONTINUE_PREFLIGHT_ONLY`. That verdict grants no authority but was an overbroad UI-pilot classification. R45 returns a HOLD for protected agent, CI, environment, config and generated paths, a distinct content/science HOLD for Markdown/MDX/TeX/Bib, and a scope HOLD for unrelated assets. Only recognized UI-source extensions (including real VitePress theme CSS/Vue files) may advance to an **advisory preflight**, never owner authorization. Invalid and mixed-scope paths fail closed.

**Limits:** This function evaluates declared strings only; it does not resolve links/case-insensitive filesystems, authenticate the caller, inspect nested policies, establish semantic correctness, run tests in a real IDE or authorize edits. Actual host agent laws and `STATUS()` → `NEXT()` → separately granted `CONTINUE()` remain sovereign. Host science integrity priorities precede optional UX changes.

## Reviewer acceptance
1. Inspect exact PR #9 head and compare the R45 cumulative code delta.
2. Run `python3 -m unittest discover -s tests -v` in a clean checkout and inspect exact-head GitHub Actions results.
3. Challenge hidden paths, CI, config, build, generated assets, scientific corpus source, path spellings, case variants and nested instructions. Record any counterexample as a new review HOLD; note source tests cannot substitute for independent review.
4. Do not merge until independent human source approval and enforceable main protection. No real local Antigravity IDE or AI-WITNESS owner execution has been witnessed. EK-003 Chromium fixtures remain separate bounded browser evidence, not deployed host changes.

**Verdict:** `R45_SOURCE_SCOPE_REVIEW_ONLY / HOST_POLICY_SEMANTICS_HOLD / REAL_IDE_HOLD / INDEPENDENT_REVIEW_HOLD / PUBLIC_RELEASE_HOLD`.
