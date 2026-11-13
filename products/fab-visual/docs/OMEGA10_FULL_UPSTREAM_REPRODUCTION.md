# FAB.VISUAL Ω10 — Complete pinned Anatomy source reproduction

**Admission:** DRAFT, SOURCE_LOCK_PASS subject to actual GitHub CI; source reproduction does **not** imply scientific, geometry, accessibility, or production release.

## Why this gate exists

Previous FAB.VISUAL versions bundle exactly four original Anatomy source modules plus the upstream MIT LICENSE, not the complete upstream tree. Ω9's 97 tests and browser checks validate the subset's bounded integration, not upstream's native test/build ecosystem. The pinned upstream Git commit is `1482e8469b0a9e0d8cc18ea2740a01423d29ae80` containing **173 blobs and 22 directories** per the GitHub Git tree API (not 173 text files; binary WebP/PDF and original assets are included).

## Independent execution design

A new least-privilege GitHub Actions job checks out the **entire** upstream repository at the exact commit into an independent directory; it does not vendor/merge this source into the FAB.VISUAL product. A pure-Python `omega10-upstream-lock.py` reconciles each checked-out path against `git ls-tree` SHA-1 blob identity, confirms an exact 173-file manifest and computes per-file SHA-256 plus a canonical root digest. It fails if any tracked file is missing, mutated, linked, or the Git HEAD differs. The original MIT copyright stays intact.

After source parity, the workflow archives the complete pinned Git source (including original PDFs/WebPs) and attempts the upstream Node.js `scripts/*.test.mjs` tests with the upstream's test-only dependency set installed using `--ignore-scripts`. It then runs all upstream example build variants, including turning-dial light verification and stress, on an ephemeral Ubuntu runner. This is **Linux reproduction of the upstream macOS recipe**, not evidence of macOS parity or browser/print equivalence. Each tested outcome is recorded and its negative outcome would remain an unresolved gate rather than a fabricated PASS.

The candidate source archive is a provenance/evidence artifact with SHA-256 manifest, not a runtime dependency or a public FAB.VISUAL release. External runners are disposable, `contents: read`, no deploy keys or GitHub write tokens retained. Material from upstream may include scripts that execute and require further security review before any privileged or local execution.

## Claim boundary

**SOURCE_PARITY** means exact tracked Git bytes. **UPSTREAM_NODE_TESTS** means the native test suite actually executed on the named runner/Node version. **EXAMPLE_BUILDS** means specific programs executed on Linux; rebuild differences must be reported. **PRINT** (Chrome/PDF) and **3D camera/route geometry** require separate named evidence. None of these entail scientific certification or installation approval.

Next: analyze source CI receipts, run source-equivalent reproduction locally only if authenticated bytes are available and safe, integrate a true volumetric connector oracle with explicit units and tolerances, preserve the live CodexStation host gate, and escalate the source-locked port/print tests. Release HOLD.
