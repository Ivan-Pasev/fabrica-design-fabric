# FAB.VISUAL Ω11H — Virtual Clock and Central Database Reconciliation

**Version:** Ω11H research candidate v0.1 · 2026-11-14  
**Source ancestry:** Original MIT wheresryan22/anatomy commit 1482e8469b0a9e0d8cc18ea2740a01423d29ae80 (173 Git blobs); stacked after Ω11G draft PR #32, original immutable. No main merge, host, permission or production changes.

## Scope and evidence

The native Google Sheet is the source of **current** gate truth. On the frozen read of 2026-11-14 at modified-time 2026-11-14T08:15:41.585Z, it contained 37 gate records (19 PASS, 6 FAIL, 10 NOT_RUN, 1 HOLD, 1 INCONCLUSIVE) and 44 evidence records. The exact Ω11G **final** SQLite at SHA256 c1d0a1293547183d4f22d1ee7d3b1026954c7a28ad066095de275e988267e693 contained 32 gates, 35 evidence references and 8 real derivative checkpoints. The current gate and evidence source rows are preserved in db/native_snapshot_2026-11-14_v0.2.json, with no fictitious source revision ID or author signature.

## Central database v0.2 candidate

db/reconcile_native_v02.py refuses in-place updates and accepts only exact SHA-matched historical input (the frozen initial v0.1 or verified Ω11G final). It compares *every* historical 32 gate record and 35 evidence record with the reviewed native Sheet source snapshot. It then **appends**, never replaces, 5 new gate events and 9 evidence rows, records native source provenance with the file modified-time, validates old and new integrity and preserves all prior checkpoint IDs. The observed 37 current statuses remain exactly 19 PASS, 6 FAIL, 10 NOT_RUN, 1 HOLD, 1 INCONCLUSIVE. Original 8 Ω11G checkpoint IDs are preserved when migrating the exact archived final DB. A separate SHA256 receipt identifies both the immutable input and new candidate file.

This is a **read-only-source, offline transactional candidate**. Google metadata exposes modified time but not a conflict-safe revision token. Therefore this is not a concurrent-safe or bidirectionally synchronized service; no human signature or release authorization is asserted. Automatic Sheet-to-DB synchronization, managed Cloudflare D1/SQL deployment and status-authority migration remain NOT_RUN.

## Clock-controlled research experiment

Source code in scripts/omega11h-virtual-raf.py is injected into separate test browser contexts **before source page load**, overriding requestAnimationFrame, cancelAnimationFrame, IntersectionObserver and performance.now with synthetic controls. It drives exactly three input timestamps at 1000/60, 2000/60, and 3000/60 milliseconds. This changes natural browser scheduling and source visibility, so it is **not** observationally equivalent to an unchanged browser. In particular: native wall-clock, browser compositor timing, some side effects of timing APIs, WebGL GPU completion, and source outside the overridden callbacks may remain uncontrolled. The three derivative checkpoints are source-linked application events only.

Six conditions per source (two unmodified page copies under the **test clock**, two minimal derivatives, two full observing derivatives) yield twelve independent fresh Chromium processes. Per-source output compares final observer application-state hashes, stage outerHTML hashes and screenshot hashes. These are *measurements*, not independent proof that the observer is causally nonperturbing. The minimal derivative itself replaces scheduling after third applied update. The full readout adds state inspection; neither uses an unchanged renderer-presented-frame barrier. The source-hashed original Anatomy checkout remains untouched.

## Gates and negation

- Source provenance: preserve 173/173 source blobs and the exact original HTML SHA.
- Database: append-only prior 32/35 source rows, retain 8 checkpoint records, validate 37/44 and SHA receipts; do not upgrade six historical FAIL records or release HOLD.
- Clock driver: separate test-only provenance and exact three monotone input timestamps; reject forged frame and uncontrolled performance.now substitution.
- Application-state repeatability: classify directly from exact machine receipt, not from theory or inferred performance.
- Unmodified real browser equivalence, zero observer perturbation, physical mesh/depth, source camera/projection, actual GPU frame presentation and cross-platform reproducibility: **NOT_ADMITTED / NOT_RUN / INCONCLUSIVE** until separately verified.

## Follow-on Ω11I

Investigate a causally bounded source clock substitution theorem and test-control coverage for browser style/layout, visibility and shader draw. Decouple application events from compositor frames. Advance database v0.3 with first-party/connected source revision checking and reviewer-authorized status admissions, without implicit deployment or signature.
