# R41 — Owner-invoked caller-IDE before/after pilot evidence

**Maturity:** draft, source-only tooling. This is an *operator kit* for recording artifacts produced by a real IDE. It does not start an IDE or certify that the artifacts are real.

## Protocol

1. Obtain the exact reviewed FDF ref `review/r41-real-host-pilot-evidence`, and verify the resolved full commit SHA before running any scripts. Read your host's local agent instructions first. Keep FDF in a separate checkout, and evidence in an owner-controlled folder **outside** the project. Do not copy secrets, unlicensed assets, private canonical research, or third-party source.
2. Before the first authorized UI edit, from the FDF checkout run:

   ```bash
   python3 tools/fdf_host_pilot.py --project /abs/path/to/current-ide-project --fdf-sha <EXACT_R41_COMMIT> --capture > /abs/path/to/evidence/baseline.json
   ```

   Record the actual local Git revision, whether the worktree is dirty, the host's own policy hierarchy and operator approval *separately*. A baseline digest is **not** an independent timestamp or witness.
3. Have the host's existing master agent execute the R39/R40 host-aware prompt: only a small authorized UI slice, preserving research content, routes, dependencies and restricted files. Capture baseline/after browser screenshots at the same desktop and mobile dimensions, the actual build log, a keyboard navigation report, and a rollback recipe. Maintain a clear repository or worktree baseline. Run the actual host checks; the evidence tool won't.
4. Create `manifest.json` **outside the host** with this exact skeleton, filling `sha256` using real file bytes (64 lower-case hex):

   ```json
   {
     "schema": "fdf.host.pilot-manifest/0.1",
     "fdf_source_commit": "<EXACT_R41_COMMIT>",
     "baseline_receipt": "baseline.json",
     "screenshots": {
       "baseline_desktop": {"path": "before-desktop.png", "sha256": "<64hex>"},
       "after_desktop": {"path": "after-desktop.png", "sha256": "<64hex>"},
       "baseline_mobile": {"path": "before-mobile.png", "sha256": "<64hex>"},
       "after_mobile": {"path": "after-mobile.png", "sha256": "<64hex>"}
     },
     "checks": {
       "build": {"path": "build.log", "sha256": "<64hex>", "reported_status": "PASS"},
       "keyboard": {"path": "keyboard.log", "sha256": "<64hex>", "reported_status": "PASS"}
     },
     "rollback": {"path": "rollback.md", "sha256": "<64hex>"}
   }
   ```

5. After local changes, run from the same pinned FDF checkout:

   ```bash
   python3 tools/fdf_host_pilot.py --project /abs/path/to/current-ide-project --fdf-sha <EXACT_R41_COMMIT> --evidence-dir /abs/path/to/evidence --admit manifest.json
   ```

   `ARTIFACT_BYTES_AND_POST_SOURCE_BOUNDED_CHECK_COMPLETE` means only that specified bytes/digests exist, bounded source changed, source scan is complete *within its declared limited scope*, and the reported checks were labeled PASS. It **does not** establish real IDE invocation, the truth of text logs, that pictures depict the project, good design, policy compliance, legitimate authorization, independent human witness, accessibility conformance or release safety.

## R41 failure modes and next admission

- Missing/changed agent-policy files, incomplete UI scan, zero source change, >12 changed eligible UI source files, mismatched picture dimensions, identical picture file pairs, absent/false checks, no rollback, symlinks, traversal and oversized or modified artifacts cause HOLD.
- If the host's existing design work naturally requires more than 12 files or the scanner exceeds its limits, request a separately scoped pilot and record HOLD—not workaround the checks.
- Human reviewer must inspect actual browser before/after, accessibility and project identity; owner must verify actual host test execution and rollback. Independent review, protected main, formal release and real IDE witness are separate authority gates. Never share sensitive evidence publicly.
