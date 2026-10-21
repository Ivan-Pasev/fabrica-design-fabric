# FDF/UAC-006 — Complete Original Installer Source Admission

**Date:** 2026-10-20 (Europe/Sofia). **Source category:** original first-party FDF() v0.2.0 distribution, unchanged. **Mode:** DRAFT source review only.

## Provenance

- Uploaded source `FDF_UNIVERSAL_ADOPTION_v0.2.0.zip` SHA256: `de833726ce83117d0305cad1af04c4fc88578bd031eb439377ff46968c70ccdf`. Original ZIP holds 14 source files plus `FABRICA_MANIFEST.json` (15 entries).
- The exact 14 original file Git blob objects and byte-identical manifest were created in GitHub and committed to `distribution/uac-v0.2/` at SHA `ea477055775d7b5ae96a1b6c1ddb80f51b877c62` in [draft PR #12](https://github.com/Ivan-Pasev/fabrica-design-fabric/pull/12).
- Manifest blob SHA: `bc2c899baa2e2ff7be4c2e6b8248dcecf5476014`, manifest SHA256: `51b3ae68b08b3f0411e323cbf1458049f2bf4e63ad5000310d70feb2de25c2f3`.
- SHA of imported original `tools/fdf_adopt.py` blob: `ce063dfc753b89af98ad1cdd3c093638e16005d9`. Imported original `tools/fdf_kernel.py` blob: `5a3e5a3bfa18398abaf385f006856439ea9a4667`.
- GitHub exact-head tree readback enumerated all original files in the isolated namespace and confirmed matching Git object identifiers.

## GitHub CI

- New `tests/test_uac006_full_distribution.py` loads the imported **original** `Adoption` and `Kernel` unittest classes from their distribution paths, plus a source-manifest regression that compares every source SHA256 and byte length.
- Source-contract GitHub Actions run [39327850489](https://github.com/Ivan-Pasev/fabrica-design-fabric/actions/runs/39327850489) concluded **SUCCESS** on the pinned import commit, logging **214 tests, OK**.
- This is a real GitHub CI run on exact committed source, not just local source tests or an unimported chat ZIP.
- The full original v0.2 source is on the draft branch, **not** public main and **not** a tagged release.

## Security qualification and limits

**Full source-import/parity gate: PASS. Original installer-production-safety gate: HOLD.**

The original `tools/fdf_adopt.py` has not been patched or replaced: its optional root-hook append still uses an existing-path `open(...,'ab')` after a separate hash check; rollback also contains an `open(...,'wb')` restoration. There is no crash-safe cross-file transaction journal and no independently qualified Windows root-hook implementation. The separate POSIX-only UAC-004 research guard is not a substitute for production integration.

For safe review, run only source inspection and `FDF` plan against a host-authorized project. Do not run `apply --root-hooks append` in any untrusted or concurrently modified workspace. Avoid general installation until a reviewed cross-platform transaction or fail-closed no-root-modification mode and real host policy checks have been verified.

## Gates retained on HOLD

- Independent human review and source/security sign-off.
- Enforceable branch protections and required CI on public main.
- Actual owner's Codex/Cursor/Antigravity/Gemini local-IDE admission and observed skill activation.
- Manual cloud ChatGPT Project/AI Studio setup, not automatic local file discovery.
- Human approval of any caller-project file mutation, kernel migration, merge or deployment.

## Next UAC-007

Implement reviewed cross-platform transaction safety or a strict no-root-hook installer mode with fault-injection tests, verify rollback/non-disruption in an actual approved project, check effective nested/global host instructions, and ask a genuine independent reviewer to assess the exact source. Keep release HOLD until then.

**Verdict:** `UAC006_FULL_GITHUB_SOURCE_PARITY_PASS / UAC006_CI_214_PASS / ROOT_HOOK_TRANSACTION_HOLD / HUMAN_REVIEW_HOLD / HOST_ACTIVATION_HOLD / PUBLIC_RELEASE_HOLD`.
