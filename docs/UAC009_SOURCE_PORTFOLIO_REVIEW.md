# UAC-009 — complete external-source portfolio and skill admission contract

Review-only proposal, 2026-10-21. This cycle consolidates 30 unique external GitHub repositories across design, motion, spatial, specification, components and QA, cross-references 15 pinned Emil Kowalski upstream skills and adds an original read-only FDF portfolio selector.

## Evidence precedence and historical limitations

1. Native FDF Drive `04_UPSTREAM_SOURCE_REGISTRY — GitHub Audit 2026-10-15`, its R11/R12/R14/R17/R25 and EK addenda, plus `09_LICENSE_PROVENANCE_AND_ATTRIBUTION`.
2. GitHub review branch `registry/upstream-emil-kowalski.v1.json`: 15 exact upstream `SKILL.md` blob pins; no bodies imported.
3. GitHub `registry/third_party_sources.v1.json` normalizes 30 historically researched repository entries. Immutable commit references are historical discovery snapshots. **No current 2026-10-21 upstream HEAD refresh or new 30-repository license verification is claimed.**
4. 5 explicit first-party `skills/*/SKILL.md` existed on the prior review branch, and 9 adaptive first-party skill templates were defined in UAC-002 `fdf_kernel.py`; these sets overlap in scope and are not 14 independent installed external skills.

## Adoption state distinction

- `CAPABILITY_MAPPED`, `SPEC_REFERENCE`, `FIRST_PARTY_ROUTING_STAGED` and `REFERENCE_BRIDGE_STAGED` represent **original FDF intelligence built using source research**, NOT a copy, fork, install or runtime activation of original third-party SKILL.md.
- `OPTIONAL_DEPENDENCY` means a runtime / testing library could be chosen only after owner-approved target-framework analysis, version/license pinning and independent dependency review.
- `PRIVATE_SOURCE_SPECIMEN` is limited to two tiny historical source-custody files from Vitesse and shadcn Taxonomy, each recorded as a prior PRIVATE study only; not a whole-repository import.
- `DO_NOT_BUNDLE`, `LICENSE_UNKNOWN` and mixed-scope licenses remain HOLD. React Bits is separately restricted under Commons Clause from the recorded audit. Unknown licenses require file-level review before copying.

## Machine contracts

- `registry/third_party_sources.v1.json`: 30 source rows, historical pins, licensing states, capabilities, distribution and host claims.
- `registry/portfolio_admission_protocol.v1.json`: evidence-required state machine from DISCOVERED to RELEASE_REVIEWED.
- `tools/fdf_portfolio.py audit`: checks 30 records, 15 pinned Kowalski subskills, license and no-install invariants.
- `tools/fdf_portfolio.py fit --intent motion`: original FDF advisory routing only; no external repo read, file modification, hidden package install or owner approval.
- `skills/fdf-upstream-portfolio/SKILL.md`: additive authored skill contract, **review branch only**.
- `injections/FDF_PORTFOLIO_CASCADE.md`: one copyable host-first read-only universal injection.
- `tests/test_uac009_portfolio.py`: fail-closed validation, negative cases and source-only contract tests.

## Scope and non-goals

Do not modify caller roots, overwrite skill directories, make third-party attribution claims, or treat a SHA, running tests or assistant-generated text as external approval. The source of truth for actual caller identity, global host policies, effective agents, platform-specific compatibility, and installed skill operation is the real owner-host session, which is not accessible here. Main and release governance remain independently gated. No distributed external third-party source bodies were added in this cycle.

## NEXT external admission

Run read-only FDF ProjectDNA in one actual approved owner project; review source-fit recommendations and licenses against the exact upstream pinned subpaths; obtain separate host-native approval for any first-party adapter installation. Verify actual IDE loading and rollback. Do not promote human review, protected main or runtime release from source-only CI.
