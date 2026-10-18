# FDF/UAC-002 — project-specific injection, skill lattice and advisory kernel

Date: 2026-10-18. This is a DRAFT review artifact stacked on prior FDF development. Existing PR authority, project design identity, science/reader integrity and external human admission gates remain unmodified.

## Architecture
Host scope → root/global/nested policy discovery → bounded ProjectDNA → skill scoring → kernel mode (AUGMENT_EXISTING_UNVERIFIED vs SCAFFOLD_ADVISORY_KERNEL) → planned additive host-specific files → separately owner-approved install → verification → model-guided bounded ProposalDNA/rollback → STATE_AND_HANDOFF.

First-party source skill family comprises project observation, governance, evolution planning, verification, design critique, accessibility review, motion planning, runtime architecture and research traceability. Universal functions are available by default; specializations depend on evidence of UI, code or research. The external emilkowalski source is pinned under the existing EK bridge and **not vendored**. No upstream agent instruction overrides caller authority.

## Model-specific bindings
Codex: `AGENTS.md` plus repo-local `.agents/skills` where enabled. Cursor: on-demand MDC rules. Google Antigravity: `.agents/rules/*.md` with YAML `trigger: model_decision` plus `.agents/skills`; legacy workflows retire October 19, 2026. Gemini CLI: `GEMINI.md` context and workspace skills. ChatGPT Project: owner pastes instructions/settings; Google AI Studio: owner imports/syncs approved GitHub source and pastes Build prompt. Do not claim cloud products automatically read GitHub dotfolders.

## Local executable package / limits
Local `FDF_UNIVERSAL_ADOPTION_v0.2.0.zip`: includes stdlib source planner/apply/verify/rollback, project-fit original SKILL.md generators, both local/cloud host templates, tests and deterministic provenance. This PR stages the injection, lattice, first-party bootstrap skill and source-only safe preview; **full ZIP code is not automatically part of this GitHub tree** unless imported in a separate reviewed code commit. A ZIP linked in chat is not a GitHub release.

Existing root instructions, user permissions and host authority outrank the installer. It does not authenticate the host, semantic global laws or model weight fine-tuning. A SHA is a consistency lock, never a human signature. Autoevolution means autonomous analysis and explicit proposals, not self-authorized file writes or deployments. No human reviewer/IDE witness/protected-main proof has been supplied.

## Next operational gate
Get an independent source review and import the complete executable package as a separate scoped commit; validate checksum and exact GitHub CI head; actual owner-host pilot in Codex, Antigravity, Gemini/Cursor; separately check manual cloud instructions in ChatGPT/AI Studio. No merge or v1 until independent authorization and governance.
