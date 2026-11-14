# FAB.VISUAL Central Evidence Database v0.1

Status: offline SQLite research snapshot, GitHub draft only, release HOLD.

## Canonical authority and locations

- Original MIT upstream wheresryan22/anatomy at 1482e8469b0a9e0d8cc18ea2740a01423d29ae80; 173 original tracked Git files.
- Source-of-truth for current 32 gate statuses: native Google Sheets FAB.VISUAL Gate Registry https://docs.google.com/spreadsheets/d/1Hn8MoTf-AFbcIZuQyskBneo4iPnA9y00HJWUrGJqn7M/edit — Gate Registry A7:H38.
- Evidence source: the same workbook Evidence Sources A2:E36, 35 records.
- Central archive folder: https://drive.google.com/drive/folders/1aaxBJfb1YnABgNuDhInMEueXisKlZO8v in the project's canonical Drive root.
- Executable schema, importer and tests: GitHub additive source in an unmerged research draft PR.
- CI product: FAB_VISUAL_CENTRAL_v0.1.sqlite, DB_SNAPSHOT_RECEIPT.json and SHA256SUMS.txt, which must be archived in the central Drive folder after exact-head independent verification.

CENTRAL means one portable queryable evidence model plus a canonical, immutable reviewed archive snapshot. It does NOT mean a live SQL cloud server, automatic Drive/GitHub sync service, deployed API, or promoted gate-source authority.

## Relational model

sources: original and observed-source IDs, revisions, authority, SHA.
gate_events: append-only gate status events with ordinal and source reference.
gate_current: highest event ordinal per gate, never overwrites history.
gate_counts: derived status totals.
evidence: append-only scoped references with limitations.
ci_runs: source-bound exact-head GitHub Actions records.
checkpoint_events: future derivative checkpoint records, EMPTY in v0.1.
metadata: source sheet, seed/schema SHA, nonadmitted frame/depth and release HOLD.

All data objects have explicit authority boundaries. Gate/evidence/checkpoint UPDATE and DELETE triggers reject mutation; permitted statuses PASS, FAIL, NOT_RUN, HOLD and INCONCLUSIVE. Foreign keys and integrity checks fail closed.

## Offline build

From repository root, with Python 3.12+ and SQLite 3.37+:

    python3 products/fab-visual/db/build_registry.py --output /tmp/FAB_VISUAL_CENTRAL_v0.1.sqlite --receipt /tmp/DB_SNAPSHOT_RECEIPT.json
    python3 -m unittest discover -s products/fab-visual/tests -p 'test_omega11g_*.py' -v
    sqlite3 /tmp/FAB_VISUAL_CENTRAL_v0.1.sqlite 'SELECT status,total FROM gate_counts ORDER BY status;'

The seed canonical_seed_2026-11-14.json is derived from live 2026-11-14 native-sheet reads and records 32 gates: 16 PASS, 6 FAIL, 9 NOT_RUN, 1 HOLD; 35 evidence references; 2 exact Ω11F CI runs. The v0.1 builder intentionally refuses a mismatched gate total or changed source pin, to prevent a stale or partial native-sheet import from being silently represented as current authority.

## Constitutional guardrails

1. Upstream original source remains immutable and separately checked against 173 Git blobs.
2. Historical screenshot and generated HTML byte parity FAILs remain FAIL; G11.12 remains HOLD.
3. Syntactically correct runtime readouts do NOT attest GPU-presented frames or 3D mesh physics.
4. Every gate and evidence record is sourced from the native Sheet and retains evidence links and limitations.
5. No unreviewed bidirectional synchronization; this DB is the archived research projection, not the active gate editor.
6. The compiler checks PRAGMA integrity_check, foreign keys, cryptographic receipt and adversarial negative tests.
7. Producing a DB snapshot neither authorizes production release nor promotes scientific results.

## Upgrade path

v0.2: source-revisioned import with reconciled append-only new gate events after native Sheet review.
v0.3: source-verified event crosswalk across CI, research drafts, screenshots and derivative captures.
Only with explicit authority: optionally deploy authenticated SQL endpoint and continuous reconciliation with RBAC, backups, conflict resolution, and append-only audit signatures. No such endpoint is installed in this increment.


## Exact-head Ω11G transactional ingestion

The full independent CI builds the initial deterministic SQLite database and records
DB_SNAPSHOT_RECEIPT.json with its **pre-ingestion** SHA256. After twelve fresh
Chromium process observations verify the original, minimal and observing source
sides, db/ingest_checkpoints.py appends only independently source-locked
instrumented derivative events and emits CENTRAL_DB_FINAL_RECEIPT.json.

- Four original-browser observations have no test hook and produce **no** false checkpoint rows.
- Four MINIMAL_DERIVATIVE records preserve exact ordinal three, with source state SHA absent.
- Four OBSERVING_DERIVATIVE records preserve exact ordinal three, with a SHA256 hash of the third source-applied state.
- The final SQLite contains 32 pre-existing Sheet-originated gates, 35 evidence references, 8 derived checkpoint records, and 3 CI receipts (two Ω11F plus the actual Ω11G run).
- **Use the final receipt's final_db_sha256 to verify the distributed SQLite file**. The initial receipt describes an earlier intermediate snapshot and must not be used to validate the final bytes.
- The browser's applied ordinal is fixed, but its RAF time remains uncontrolled: application state equivalence is INCONCLUSIVE, and actual renderer presentation remains NOT_ADMITTED.
- SQLite is versioned and archived; no always-on service, automatic Google Drive synchronization, or production release is implied.

Research decision: products/fab-visual/docs/OMEGA11G_CENTRAL_DATABASE_CHECKPOINT_DECISION.md.
First independently verified full ingestion CI:
https://github.com/Ivan-Pasev/fabrica-design-fabric/actions/runs/43573628843.
Canonical archived database and receipts:
https://drive.google.com/file/d/1ul7zcuKHzsGHjItxiqRsahEzsOJyTJ8k/view.
