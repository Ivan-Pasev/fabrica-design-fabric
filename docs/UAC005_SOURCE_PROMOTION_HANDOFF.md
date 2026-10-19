# UAC-005 — exact-source promotion handoff, owner-run and unmerged

## Live source state
Current FDF Universal Adoption v0.2 ZIP SHA-256 is de833726ce83117d0305cad1af04c4fc88578bd031eb439377ff46968c70ccdf. It contains 14 original first-party source files plus FABRICA_MANIFEST.json. The complete 14 sources have NOT yet been imported to this GitHub draft branch; older UAC-003 SHA ledger is authoritative to check exact files.

This new research-only script research/uac005/tools/uac005_promote.py can import the verified archive onto an owner-controlled, clean local Git checkout, in distribution/uac-v0.2/. It does NOT mutate the app root rules, run npm, connect to any model provider, commit, push, merge, publish or deploy.

## Operator workflow
1. On the real local machine, check out review branch review/uac002-fdf-multimodel-bootstrap. Verify no uncommitted work and obtain the original trusted FDF_UNIVERSAL_ADOPTION_v0.2.0.zip.
2. From the FDF checkout or a separately trusted utility directory, inspect the tool and run:
   python research/uac005/tools/uac005_promote.py plan --archive /path/to/FDF_UNIVERSAL_ADOPTION_v0.2.0.zip --checkout /path/to/fdf-git-checkout
3. Review exact 14 source paths, hashes, Git HEAD, target directory and plan SHA. Owner invokes apply --archive ... --checkout ... --approve-plan EXACT_PLAN_SHA only after separately granting permission.
4. verify --checkout ... independently recomputes all staged source hashes and rejects tampering.
5. Operator manually inspects Git diff/untracked files and makes an explicit separate commit on the draft review branch, then runs full original v0.2 tests in CI. No automated push or endorsement implied.

## Fail-closed boundaries
- Hard-pinned whole ZIP SHA-256 and 14-file manifest SHA. Refuses ZIP traversal, duplicate entries, unsafe names and source symlinks, oversize input or extra files.
- Requires a true clean Git checkout root and nonexistent import target. Import is staged to a temporary same-parent directory then renamed. Refuses duplicate plans and mismatched plan digests.
- It is NOT adversarial-filesystem safe: parent path replacement during write, multi-operator races, commit/signature authentication, crash durability on all OSes and Windows host qualification remain open. Do not use against an untrusted concurrent shared checkout.
- Test fixtures in CI generate a synthetic ZIP and patch the test module PIN locally; they prove algorithm contracts, not that GitHub contains the full actual v0.2 source. Actual local original ZIP hash and clean-extraction v0.2 tests were verified separately.
- Do not claim GitHub full-source parity until the actual 14 files are present on a new exact PR head, their Git blob bytes match SHA ledger, and full v0.2 tests pass in connected Actions.

Release gate: SOURCE_IMPORT_TOOL_REVIEWED_BY_MACHINE / LOCAL_TESTS_PASS / GITHUB_FULL_V02_IMPORT_HOLD / HUMAN_REVIEW_HOLD / REAL_IDE_HOLD / PROTECTED_MAIN_HOLD / RELEASE_HOLD.
