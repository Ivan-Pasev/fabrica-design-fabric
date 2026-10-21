# FDF/UAC-007 — additive-only transaction candidate

**Research candidate; not a released installer.** This distribution contains the byte-preserved original FDF v0.2 sources and adds `tools/fdf_safe.py` plus crash/rollback tests. The original `tools/fdf_adopt.py` and `tools/fdf.py` remain unchanged; use the new safe entrypoint explicitly.

## Read-only review

```shell
python tools/fdf_safe.py plan --project /path/to/actual-project --platforms codex,cursor,antigravity,gemini
```

No existing `AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, root policies, or matched existing adapters are rewritten. Plan output includes `transaction_sha256`, proposed Fabric-owned new files, directory changes and `release: HOLD`. An exact plan SHA is **not** proof of owner identity or host approval.

## Owner-authorized cooperative-workspace rehearsal only

Only after the owner and current host instructions separately approve the exact plan, and **only when no competing process is changing the workspace**:

```shell
python tools/fdf_safe.py apply --project /path/to/actual-project --platforms codex,cursor,antigravity,gemini --approve-plan EXACT_TRANSACTION_SHA256 --trusted-single-writer
python tools/fdf_safe.py status --project /path/to/actual-project
python tools/fdf_safe.py rollback --project /path/to/actual-project --approve-plan EXACT_TRANSACTION_SHA256 --trusted-single-writer
```

`--root-hooks append` is always REFUSED by this entrypoint. The prewrite `.fabrica/UAC007_TRANSACTION.json` journal records only planned paths and hashes; it does not store project policy text. After a crash, `status` reports `INTERRUPTED_RECOVERABLE` when all existing managed files match the journal and no manifest exists. Owner-authorized rollback removes only exact-hash managed files and directories absent before the operation. If any file is modified, rollback FAILS CLOSED without deleting it. The operation does not auto-retry an interrupted installation.

## Limits

- Windows-native execution and NTFS/OneDrive race behavior are **not tested**. Python uses portable APIs where available, but cross-platform release qualification is HOLD.
- Concurrent malicious or uncooperative writers are out of scope, as are power-loss ordering guarantees of all filesystems and abrupt truncation of the journal itself. O_EXCL creates and component symlink checks reduce accidental overwrites but do not prove race freedom on Windows.
- Every read uses bounded, static files. Host/global/nested instruction semantics, actual installed-skill recognition and model identity are NOT authenticated.
- A new FDF() host pilot requires project-specific owner review, observed IDE rule loading, real tests, and rollback evidence before public release.

## Build checks

`python -m unittest discover -s tests -v` — 50/50 local tests PASS (37 original + 13 UAC-007), including injected interrupted transactions and owner edits. GitHub import is an independent review gate; do not equate this ZIP with a merged branch.
