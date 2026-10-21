# UAC-007 cooperative installation transaction — source and gate review

## Preserved invariant
Original v0.2 installer bytes are unchanged. A **new** CLI uses its template/plan source only; default transaction creates new Fabric-owned files and never opens preexisting `AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, or an existing managed integration for writing.

## Evidence matrix
- Exact staged v0.2 ZIP SHA256 `de833726ce83117d0305cad1af04c4fc88578bd031eb439377ff46968c70ccdf` preserved in pack.
- 37 original regression tests PASS, 13 new transaction tests PASS, 50/50 overall PASS locally, clean extraction recheck required before archival publication.
- PREPARED journal written before application files; O_EXCL file creation; contents and target file hashes checked after controlled installation.
- Recovery scans journal; incomplete but hash-valid files can be rolled back only by explicit matching transaction digest and single-writer acknowledgment. Modified file, symlink, plan drift, existing installation: HOLD.
- Directory inventory records which paths were missing before installation; existing empty caller directories remain after rollback.

## Unclosed
1. Whole-run atomic commit remains unavailable: each file is created separately, and abrupt loss can leave an incomplete transaction. This is **recoverable where hash-valid**, not atomic.
2. Concurrent malicious path replacement, Windows junctions/reparse points and network-mounted filesystem guarantees are not independently validated. Native Windows test matrix: PENDING.
3. Journal forgery and local privilege compromise are out of scope. Approval digest is not an identity token.
4. `fdf_safe.py` is not wired into original `fdf.py`; it is a distinctly invoked candidate. Existing v0.2 root-hook code remains unsafe for general rollout.
5. Independent human review, effective protected main, owner-host deployment, cloud adapters and public release remain HOLD.
