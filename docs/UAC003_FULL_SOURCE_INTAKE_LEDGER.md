# UAC-003 Full Source Intake Ledger — 2026-10-19

Archive verified in execution container: `FDF_UNIVERSAL_ADOPTION_v0.2.0.zip`
- Whole archive SHA-256: `de833726ce83117d0305cad1af04c4fc88578bd031eb439377ff46968c70ccdf`
- 15 ZIP members (14 source items + FABRICA_MANIFEST.json); 32,893 bytes.
- Clean extraction: `python -m unittest discover -s tests -v` => **37 tests, OK**.
- This record **does not claim GitHub source parity**. Local uploaded files cannot be directly read as source strings by the connected GitHub write connector; source-import is still pending.

| Local source item | SHA-256 | Bytes |
|---|---|---:|
| FDF_UNIVERSAL_INJECTION.md | 022af5ff9a7d1cc563359cae404b92ae68d90f55d405b783b8223e2c5658537f | 5525 |
| README.md | a99b33179afe416bfc19ecf824b9d5be5026fec4586bf5af7ffd1d64bc0f9289 | 5004 |
| docs/FDF_KERNEL_SPEC.md | 7fc1ac1dcac7eea5888058d9f13f933d69d186719ac8549df53632b52b3bc262 | 3123 |
| docs/MACHINE_HANDOFF.md | b3c82ade58c157c358599e85675780e042f229e0ad6997d4b701a2112f65f8f3 | 1604 |
| docs/PLATFORM_COMPATIBILITY.md | e5f3006aab2eaaca01d601de6f6424e663b1d889707d9014a36398d096efb1e8 | 1972 |
| docs/THREAT_MODEL_AND_GATES.md | 8ad7ebf90dbb8bf8a7e227ed69761b4b7c3a062c02de4f2ce301556385d1fc4c | 2957 |
| examples/SCENARIO_REPLAY.json | 08c5f2cc37da0bf7edc258c9a5102047d6fa86dc156ccec1046e6499d8a2f6a7 | 1707 |
| examples/run_scenarios.py | 46f272f38644e339f5541741dd1d9c26e6feb4ad8b4f4d6da7af1d349edaf1fa | 2370 |
| skills/fdf-universal-adopter/SKILL.md | 8d9e476b0cfaf2c93e79d2dd65ebe9deec56423c771cc06e9b691b9c1a74563c | 2115 |
| tests/test_fdf_adopt.py | 23d3676870fe2e83e6b63b83a1a7a7c1f302b76422b7dcaac7256d7f49c0d581 | 8852 |
| tests/test_fdf_kernel.py | c30f7fd6b97e5e05e7bf1627fb1ff4b26a9bb1f5726d1666b3c47855519119e1 | 5489 |
| tools/fdf.py | e3af3bb4301610a08b6fb9a8f77a889f9724493a127454ca850563d01a4342d2 | 2803 |
| tools/fdf_adopt.py | 48abe77b12a91d94bae66e06234204d2b7d6a44b536b8f365209e4bc54a8ca71 | 19823 |
| tools/fdf_kernel.py | b07c93acb4119a8138a7af5fc7e9f147fbe4e1419317a023094085f2fa7b76bc | 9390 |

## Focused R&D security review
- `apply` uses `O_EXCL` for new managed files and root precondition/digest locks, but root hook append uses `open(path, "ab")` after a prior check: susceptible to a local symlink replacement race / TOCTOU. Needs no-follow directory-fd hardened writes or fail-closed host lock design before untrusted-workspace approval.
- `rollback` writes restored root content using `open(path,"wb")` after verification: same concurrent replacement limitation, and failure during multi-file rollback can produce partial state without an operation journal.
- Existing root/global/nested policy *semantics* are not authenticated by static detector; source snapshots and hashes must not be promoted to host authority.
- The v0.2 package does not implement a safe in-place upgrade from existing managed state, intentionally HOLD on second installation.

## Required next work
1. Owner-authorized local Git import to the exact draft PR #12 branch, placing full source under `distribution/uac-v0.2/` or equivalent clearly scoped namespace, preserving FDF existing scripts. Check every SHA against this ledger.
2. GitHub Actions run full `test_fdf_adopt.py` and `test_fdf_kernel.py` at the exact imported head.
3. Harden root-hook TOCTOU and interrupted rollback; independent review before real host installation.
4. Witness an owner-controlled IDE admission in the actual existing project, then test Codex/Cursor/Antigravity/Gemini and manual cloud adapters.
5. Remain DRAFT / NO MERGE / NO DEPLOY until branch protection and human reviews.

**Status:** `ZIP_EXACT_PASS / CLEAN_TEST_37_PASS / GITHUB_FULL_SOURCE_IMPORT_HOLD / HUMAN_REVIEW_HOLD / REAL_IDE_HOLD / RELEASE_HOLD`.
