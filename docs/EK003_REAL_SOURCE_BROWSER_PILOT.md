# FDF/EK-003 — Actual GitHub caller source, local Chromium A/B, admission HOLD

**Date:** 2026-10-18. **Type:** real external source observation, NOT witnessed owner IDE execution. **Caller:** [AI-WITNESS / IRP-1](https://github.com/Ivan-Pasev/AI-WITNESS), Git head `a51f8cae1d239feaf3c418ff68f827ffecc602cd`.

## Pin and license

GitHub-confirmed exact blobs: `public/verifier/index.html` = `e8b75e6d9e07938605e4fe9b471c1855fb1f7b26`, `public/verifier/app.js` = `069be827cea9e44200bd853f23513b87dd8a15ef`. The caller's own repo declares Apache-2.0. No caller changes or npm installs were made. This FDF PR contains only this original evidence summary; test copies/screenshots and patch stay in the separate session evidence capsule.

## Host policy and source-scope admission

The entire accessible GitHub source tree at the caller commit contains no `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `AI_CRITICAL.md`, `.cursorrules` or `.github/copilot-instructions.md`. This does **not** prove the actual local IDE has no global or uncommitted rules. It means the R40/KBI host-policy source intake cannot be promoted from remote GitHub evidence; FDF/EK-002's admission remains `HOLD_HOST_POLICY_DISCOVERY_UNKNOWN`. The FDF bridge was **not** executed or admitted in the owner's local IDE.

## Observations against exact source

Local Playwright/Chromium loaded exact Git source bytes using `set_content` + `add_script_tag` (not a deployed site). Reversible candidate modifications were made **only in browser memory**, with a generated patch *not applied* to caller Git.

| Source-anchored issue | Baseline observation | In-memory proposed change / remeasurement |
| --- | --- | --- |
| [`app.js:7`](https://github.com/Ivan-Pasev/AI-WITNESS/blob/a51f8cae1d239feaf3c418ff68f827ffecc602cd/public/verifier/app.js#L7) `innerHTML` interpolates an untrusted report field | Benign `<em>` from pasted W2 policyVerdict appeared as an HTML element | Construct strong/br/text nodes and use `textContent`; markup displayed literally, no inserted `<em>` |
| [`index.html:11`](https://github.com/Ivan-Pasev/AI-WITNESS/blob/a51f8cae1d239feaf3c418ff68f827ffecc602cd/public/verifier/index.html#L11) card lacks unbroken text wrapping | A 66-character hex-like verdict yielded document scroll widths 625px at 320/375, 1349px at 1280; a 130-character verdict yielded 1200px at 320/375, 1924px at 1280 | Add `min-width:0;overflow-wrap:anywhere` to card; 320/375/1280 widths held exactly with no horizontal overflow in controlled browser replay |
| [`index.html:18–19`](https://github.com/Ivan-Pasev/AI-WITNESS/blob/a51f8cae1d239feaf3c418ff68f827ffecc602cd/public/verifier/index.html#L18-L19) no explicit associated form labels | `labels.length=0` for JSON textarea and file input | Add `label for=` elements; browser DOM `labels.length=1` each |
| Semantic boundary | "SEMANTIC TRUTH: NOT PROVEN BY IRP-1" present | Still present |

The token strings are bounded *stress test* data and do not prove real policy verdicts normally contain hex IDs. The UI handles pasted JSON without an observed field-length cap. HTML parsing is a concrete trust-boundary risk, **not** a demonstrated production exploit. Chromium local rendering is not an assistive-technology audit, hardware/mobile-device qualification or authorized local IDE session.

## Kowalski reference routing

Design concepts: upstream `break-ui` skill (pinned blob `091a28d488662d2451131f1aaa60a6dcd2391932`) for worst-case UI data and `emil-design-eng` for craft/accessibility. The reference selection is a **human-authored design mapping based on source**; KBI's executable host route cannot pass without caller host policy discovery. No upstream installation, prompt auto-execution or caller source edit.

## Proposed owner-gated disposition

One reversible two-file proposal: (1) text-node safe rendering; (2) unbreakable status wrapping; (3) explicit field labels. Before implementation obtain current caller HEAD/host policy proof, explicit owner approval, and verify exact file digests. The owner should use the host's existing `STATUS()` then read-only `NEXT(UX@verifier)`, followed by separate optional `CONTINUE()` only if host admission permits. Tests required: real keyboard focus, screen reader name checks, user data shape, mobile 320/375/1280, no horizontal overflow, no DOM injection and actual app functional regressions. Rollback: revert the two authorized file edits.

**Verdict:** `EXACT_GIT_SOURCE_VERIFIED / CHROMIUM_OBSERVATION_PASS / CANDIDATE_IN_MEMORY_BROWSER_PASS / FDF_HOST_POLICY_HOLD / REAL_IDE_HOLD / REVIEW_HOLD / PUBLIC_RELEASE_HOLD`.
