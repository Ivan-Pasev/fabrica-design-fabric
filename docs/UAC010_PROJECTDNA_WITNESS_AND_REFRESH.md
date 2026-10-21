# UAC-010 — Local ProjectDNA witness + three-source refresh review

Date: **2026-10-21**. UAC-010 is a **read-only admission candidate** stacked on PR #13. Project-independent AI skill routing is not actual model-weight fine-tuning.

## Project authority and privacy boundary
The owner runs `tools/fdf_projectdna.py witness --project <absolute project path> --host cursor --intent design` in the real IDE environment. It emits JSON to standard output; **no files are modified intentionally**. Only observed policy relative paths, lengths and hashes are emitted, never policy text or absolute caller path. It identifies root/nested sources by a bounded filesystem search and records common adapter directory signals, Git HEAD/dirty evidence when possible and marker-based framework signals. The declared host label is NOT authenticated; global editor/user rules and effective instruction precedence remain UNKNOWN. It does not execute project package scripts, invoke an LLM, install any skill, clone a repository or send data externally. A digest of its output is **integrity metadata, not a signature, authorization or proof that a project is safe**.

The user should review/redact the stdout JSON for private project names, policy paths, hashes, commit SHA or framework signals before transferring it to a connected agent. The tool is not a security boundary against hostile concurrent filesystem changes, unreadable trees, path ancestor symlinks, a malicious Git executable/configuration, Windows junctions or OneDrive. Symlinked policy paths are refused as unsafe; global host policy unavailable remains UNKNOWN, not ABSENT.

## Source refresh: selected three donors only
`registry/uac010_selected_source_refresh.json` records direct 2026-10-21 GitHub default-branch/commit and `LICENSE` evidence:
- Emil Kowalski Skills: pinned `2d228630ba1446365f614a108cb8252f1feda202`, current `main` same, LICENSE MIT blob `57b46f1fd11dc62351ea548104a88aa3f659c11b`. Source-only match; 15 upstream skills are not installed.
- Impeccable: historical `d631a8827f99414d2b6daba4ef08b7f8701751d7`; observed new `dad8dbb3aac21ad1fa236c110315ef4abece23e8`, 76 commits ahead, compare returned 300 files (capped); LICENSE Apache-2.0 blob `bb3f6d23b1f8025514a62a12b51b47d73e3c9aa9`. Skill paths changed, requiring review.
- Taste Skill: historical `f624f37a8c650b9cc550253104925efe4c8de246`; observed new `6010f91a9935f1c167dfc500fb1a475681892e6b`, 28 commits ahead, 73 changed files; LICENSE MIT blob `48a2f6640b81ff8eca9ce7f6a96337692713ef5b`. Plugin integration changes require review.

No historical pin was altered, no upstream bodies copied, and license observations are at repository/root-file level only. A full audit must cover selected executable scripts, transitive dependencies, source subpaths and specific redistribution requirements.

## Rehearsal and proof
The test suite uses synthetic temporary project trees. It verifies read-only metadata extraction, policy content non-disclosure, exact but unauthenticated digest receipts, absence of invented host claims, selected-source license and drift restrictions. This **does not constitute the requested real user IDE witness**. To close that gate, an authenticated local operator must inspect actual local/global/nested IDE rules, run the command in the intended caller workspace and separately approve an additive FDF proposal, then observe native model skill discovery and reversible effects.

## Operational gates
GitHub source tests on exact PR commit may qualify implementation behavior, not host admission. Independent reviewer, protected main, release, live source installation and hostile Windows junction/concurrency remain HOLD. Existing 30-source atlas and host-first KBI contracts stay authoritative; user project files should not be edited just because FDF() is mentioned.
