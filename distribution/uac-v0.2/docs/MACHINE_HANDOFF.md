# Portable machine handoff / agent.md role

## Invariant spine

1. Source of truth is **the current caller project's own policy tree and code**. FDF adds optional design competence, never replaces root intelligence.
2. Distinguish `PLAN_NO_WRITES`, `ADOPTION_APPLIED_TO_DISCRETE_PATHS`, `INSTALLED_SOURCE_HASHES_MATCH` from `ACTUAL_IDE_ADMISSION`, `HUMAN_APPROVED_DESIGN_CHANGE` and `RELEASE`. Only first three are measurable by this adopter.
3. Under long-running agentic host workflows, read host `STATUS()` and policy priority before every FDF `NEXT()` proposal; do not infer that any FDF advice grants `CONTINUE()`, `PUBLISH()` or `DEPLOY()`.
4. Keep project secrets, credentials, notes, authorial source and any vendor-only media outside FDF export. Preserve original code identity.
5. Avoid model-specific overprompting. Keep always-on pointers small; activate detailed skill context on demand.

## Next development sequence

- R&D separate versions of ProjectDNA detection that are bounded to caller-approved paths and attest real host policy precedence.
- Add optional verified framework adapters and full exact-source ProposalDNA for source edits, not just a static integration installer.
- Allow coordinated, versioned upgrades only with manifest history, diff review, safe recovery, signed provenance, and actual IDE user approval.
- Benchmark on diverse real projects (legacy monorepo, new prototype, mature institutional site, Python/React hybrid, Expo/mobile app) with non-regression and measurable UX evidence.
- Keep external review/release gates HOLD until genuine independent approval.
