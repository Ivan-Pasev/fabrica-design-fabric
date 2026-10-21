# FDF/UAC-004 — root policy hook hardening research, not installer integration

Date: 2026-10-19. Review target draft PR #12. Scope: *research-only POSIX root-hook proof of concept*, not a replacement for full portable installer v0.2. No actual owner project or IDE was touched.

## Exact source/provenance
- UAC-002 standalone source ZIP: `FDF_UNIVERSAL_ADOPTION_v0.2.0.zip`, SHA256 `de833726ce83117d0305cad1af04c4fc88578bd031eb439377ff46968c70ccdf`; 14 source files + 1 manifest, CRC clean. Clean archive tests **37/37 PASS**.
- UAC-003 ledger: `docs/UAC003_FULL_SOURCE_INTAKE_LEDGER.md`. Its **full installer source parity remains HOLD**; only a source manifest is in the PR.
- Independent UAC-004 prototypes are under `research/uac004/` with a root CI test shim `tests/test_uac004_root_guard.py`. The prototype is **not used** by v0.2 `tools/fdf_adopt.py`; copying it into an owner's workspace by itself is NOT an install/admission instruction.
- Local exact SHA256: `research/uac004/tools/fdf_root_guard.py` = `eb4d5edfe44ab6e747f56ff6774d6b89e927168c29ee5e36622200b3972fffc6`; `research/uac004/tests/test_fdf_root_guard.py` = `2f720cd0fda9c6058256ae9badd28683ce6e0fd9adafd100a4c2afa84ec953ed`.

## Bounded improvements explored
1. POSIX file-descriptor paths anchored with `O_DIRECTORY|O_NOFOLLOW`; no-follow checked-in root AGENTS.md or GEMINI.md.
2. Only regular small files; compare owner source SHA256 before append, check fd identity and acquire advisory `flock` lock. SHA consistency is not proof of human identity.
3. Write and fsync a **pre-mutation digest journal** in `.fabrica`, containing only before/after/tail digests, size, status; no policy source content.
4. On supervised recovery, inspect whether operation was never applied, applied intact, or drifted/partial. Only digest-exact intact append is eligible for truncated recovery; changed owner file is HOLD, not clobbered.
5. Read/write code explicitly **fails closed on Windows** or unsupported no-follow/locking hosts. No claim of Antigravity or Cursor on Windows support. Local Linux source tests 8/8 PASS, plus v0.2 suite 37 PASS = 45 local tests.

## Still unsafe / excluded from promotion
- Multi-path crash consistency is not yet provided: individual root journals do not form a single atomic all-adapter transaction.
- OS-level permission escalation and concurrent processes that ignore advisory locks remain outside guarantees. Path parent swaps are mitigated with anchored descriptor in this root-only prototype, but not in current v0.2 generated skill-file installation paths.
- Crash during a partial regular-file write requires operator review and may not be automatically restorable.
- Independent Windows implementation and Windows/PowerShell tests are absent.
- **Critical:** The prototype is not wired into full v0.2 installer. The full installer root-hook `open(...,"ab")` and rollback `open(...,"wb")` risks therefore REMAIN. Do not install v0.2 into adversarial shared workspaces on the strength of these tests.
- Human acceptance, policy semantics/global rules, protected-main enforcement, actual Codex/Antigravity/Gemini/Cursor live host invocation and public release all remain HOLD.

## Exact next steps
1. Import complete 14 original installer files into isolated `distribution/uac-v0.2/` namespace with SHA parity and source CI; no unmanaged edits to prior FDF kernels.
2. Design secure cross-platform transaction strategy; either owner-controlled root pointer edit under host-native installer with independent review, or default **no existing-root mutation** on unsupported OS.
3. Replace v0.2 write/rollback paths only after formal review, coherent transaction journal and fault-injection tests.
4. Run actual local IDE live pilot on an owner-authorized existing project, inspect real nested/global host instructions, prove installed skill discovery and reversible ProposalDNA, then independent review and effective protected-main governance.

**Disposition:** `LOCAL_UAC004_GUARD_8_PASS / FULL_LOCAL_COMBINED_45_PASS / GITHUB_RESEARCH_CI_PENDING / FULL_INSTALLER_SOURCE_PARITY_HOLD / WIN_HOST_HOLD / RELEASE_HOLD`.
