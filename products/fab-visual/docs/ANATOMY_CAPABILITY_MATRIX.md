# Anatomy: preserved complete capability inventory (pinned Ω7)

The upstream original Git tree at the pinned SHA contains **173 tracked blobs and 27,648,351 blob bytes**, including nine example directories (not merely the eight originally named in the v1.0 release), nine PDF sheets, and 45 `*.test.mjs` source tests. These counts describe source presence; functional verification is separate.

| Capability | Upstream source anchors | Preservation via submodule | Functional acceptance gate |
|---|---|---|---|
| Skill and creative workflow | `SKILL.md`, `agents/openai.yaml`, `references/craft.md` | exact byte-preserved | integration in actual agent host NOT_RUN |
| Isometric SVG + CSS | `kit/iso-kit.mjs`, `.ts`, `.css` | exact | existing examples regenerate byte-identically |
| Round and curved solids | `kit/lathe.mjs` | exact | Node tests and 3D geometry sweep |
| Tubes, pipes, wires | `kit/tube.mjs` | exact | actual clearances, mounts, thin wire adversarial |
| Spatial audit | `kit/audit.mjs`, line-end scripts | exact | independent sampling-vs-analytic counterexamples |
| WebGL effects | `kit/gl.mjs`, `gl-shared.mjs` | exact | Chrome on/off + shader no-pop visual evidence |
| 3D rotation beta | `kit/turn*.mjs`, `turn-build.mjs`, `turn-audit.mjs` | exact | orbit audit and turn-check order/lines/perf |
| Experimental performance | `kit/canvas-painter.mjs`, `turn-fixed.mjs` | exact | opt-in performance regression; no default replacement |
| React integration | `kit/react/draw.tsx`, `live.tsx` | exact | pinned React/TS type and UI testing |
| Headless Chrome QA | `scripts/capture.mjs`, `drive.mjs`, `turn-check.mjs` | exact | independent browser screenshots and action tests |
| Printable A4/Letter PDF | `scripts/print.mjs`, `print-sheet.mjs`, example sheets/PDFs | exact | PDF generation + output compare/preview |
| Community publication | `scripts/publish.mjs`, `references/publish.md` | exact | dry-run only; no unauthorized submission |
| Fingerprints, provenance | `scripts/fingerprint.mjs` | exact | compare complete source, not fingerprint subset only |
| Gallery and example tutorials | 9 `examples/*` directories, prebuilt outputs | exact | rebuild all supported examples, both themes |
| Tests/CI/evals | 45 `scripts/*.test.mjs`, `evals/evals.json`, upstream CI | exact | all native tests on full checkout |

### Status (do not collapse)
- SOURCE: pinned full-tree pointer is present in the FAB.VISUAL repo branch.
- SOURCE CHECKOUT: only PASS after checkout on an external runner and independent hash reproduction.
- FUNCTION: original upstream test suite and example parity must be executed in CI before claiming PASS.
- WEBGL/3D/PRINT: require separate measured workflows. Not all of these were tested in Ω5/Ω6.
- SCIENCE: certification NOT_RUN; no physics or real mechanisms validated by source presence.
