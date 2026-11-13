# Anatomy upstream acquisition and license control

Source of truth: https://github.com/wheresryan22/anatomy
Pinned commit: `1482e8469b0a9e0d8cc18ea2740a01423d29ae80`, dated 2026-10-18.
MIT license, copyright (c) 2026 Ryan.

GitHub tree inventory at pin: **195 entries = 173 blobs + 22 directories**; no truncated tree response. The full inventory (path, Git blob SHA and file byte count) is maintained separately in Drive's Source/License branch. This inventory is **not the same as downloading and reading every blob**.

Review map:
- `SKILL.md` + references: process and craft rules, agent skill loading.
- `kit/iso-kit.ts`, `kit/iso-kit.mjs`, `lathe.mjs`, `tube.mjs`: physical geometry, projection, surface representations.
- `kit/audit.mjs`: screen-space overlap, support and depth-order audit; finite sampling and thin-wire blind spot.
- `kit/turn.mjs`, `turn-build.mjs`, `turn-audit.mjs`: beta true-3D articulation and orbit audit.
- `kit/gl.mjs`, `gl-shared.mjs`: WebGL layering and projection.
- `kit/canvas-painter.mjs`, `turn-fixed.mjs`: experimental alternative rendering paths.
- `kit/react`: React server/client interface.
- `scripts/capture.mjs`, `drive.mjs`, `lines.mjs`, `print.mjs`, `publish.mjs`: browser verification and distribution tools with security boundaries.
- `examples/ripple-tank/model.mjs`: math/visual count boundary discrepancy.
- `scripts/publish.mjs`: two same-theme pages can collide in page registry (#89).
- Upstream PRs #129, #149, #151 open on 2026-11-13; not merged into locked main.

### Upstream execution policy

When authorized, clone into a separate unprivileged workspace, checkout the exact commit, validate `git rev-parse HEAD` and LICENSE, run package-free regression tests, browser audits in an isolated worker, and record SHA-256 snapshots. No auto-clone or high-privilege browser invocation from this reference runtime.

### Portfolios and mutation

1. Acquire and license-check source (path inventory done; complete file-by-file reproduction pending).
2. Map modules to semantic, geometry, rendering, browser audit, export and risk layers.
3. Bind a SHA-locked adapter and capture independent CI receipts.
4. Contribute upstream corrections when possible without fork identity confusion.
5. Only then evaluate optional vendoring or permanent fork with original MIT notices.


## Ω5 exact-source partial absorption — 2026-11-13

Exact Git blob SHA for four original source files and original MIT LICENSE was verified after conversion transport normalization, and native code was directly executed. This resolves a **narrow executable adapter** but not full upstream absorption. See `vendor/anatomy/SOURCE_LOCK.json` and `docs/VERIFICATION.md`. The 173-blob original tree inventory stays authoritative for the full-scope acquisition program. Other 168 blobs have **not** been bundled. Pull requests not merged at pin remain research leads, not accepted patchset. The native audit reproduces a thin-wire false negative; independent ray-vs-AABB checks therefore report INCONCLUSIVE rather than accepting absence of sampled overlap as evidence of full visibility correctness.
