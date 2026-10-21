# UAC-011 — Owner-controlled FDF skill admission pilot

2026-10-21 · GitHub DRAFT review material · No caller IDE access occurred in this ChatGPT session.

## What UAC-010 already proves
UAC-010 source and CI checks verify a metadata-only ProjectDNA witness, not real host rule loading or project adaptation. UAC-009 provides thirty research references (not thirty installed skills). UAC-007 provides an additive-only cooperative installation candidate, NOT universal protected installation or root instruction rewriting. Retain those boundaries.

## Recommended 0-write real-workspace pilot
Open **one** selected existing project in the actual IDE. Confirm its repo and active instructions. Separately check global/editor/team rules and current existing root instruction priorities. From a reviewed FDF checkout *outside the caller project*, run the UAC-010 read-only tool only if allowed:
```
python tools/fdf_projectdna.py witness --project "ABSOLUTE_ACTUAL_CALLER_ROOT" --host antigravity --intent design
```
Before sharing output, redact private project names, relative paths, Git SHA and policy hashes as appropriate. The command does not verify that Antigravity is actually the host; `--host` is self-declared.

Next inspect any **already-installed** FDF skill through native host controls. If absent, return STOP_INSTALLATION_AUTHORITY_REQUIRED and supply an exact additive, owner-approved proposed file plan; do not silently copy source into the project. If present, inspect native UI/commands for discovery and activation and ask the model to produce **one read-only project-specific ProposalDNA**. Owner compares the proposal to actual code and rules. Independently inspect git diff/status to confirm no unintended edits.

## Native checks and current public documentation
- Antigravity IDE: skill locations `.agents/skills/<name>/SKILL.md`, and its Agent side-panel Customizations list. Source: https://www.antigravity.google/docs/skills?tab=ide
- Gemini CLI: workspace `.gemini/skills` or `.agents/skills`, `/skills list`, explicit `activate_skill` and user consent. Source: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md
- Cursor: versioned `.cursor/rules/*.mdc`, Rules UI and active-rule indicators; rules evidence is NOT proof a separate Agent Skill was loaded. Source: https://docs.cursor.com/context/rules-for-ai
- Codex: confirm current product-native skill detection in the user's actual running tool and AGENTS.md hierarchy; local source files are not sufficient proof.
- ChatGPT Projects and Google AI Studio: manually supplied context/source only, not inherited local skill activation.

## Minimum independently reviewed evidence
1. Redacted ProjectDNA output with exact originating SHA and known unknowns.
2. Exact first-party skill source Git commit and digest; locally observed skill path.
3. Real host interface/CLI record of skill discovery and actual activation; distinguish model self-report from external observation.
4. One project-specific read-only proposal whose compatibility with existing rules is independently checked.
5. Git status before/after, and rollback evidence if a separately approved installation was performed.
6. Owner/operator decision and independent review recorded outside assistant-generated text; retain private raw evidence off the public repo.

There is no cryptographically authenticated owner witness in FDF today. A filled checklist, hash or self-reported JSON must never automatically promote the integration to PASS. No merge, deploy or governance change follows from this guide.

## Next meaningful closed gate
`REAL_PROJECT_SELECTED → HOST_NATIVE_SKILL_DISCOVERY → OBSERVED_ACTIVATION → FIRST_READ_ONLY_PROPOSAL → OWNER_REVIEW`. Each state requires real, source-linked evidence; absent owner-local evidence remains HOLD. No further synthetic CI run is a substitute.
