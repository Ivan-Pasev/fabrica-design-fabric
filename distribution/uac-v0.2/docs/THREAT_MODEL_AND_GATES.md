# Operational bounds and threat model

**Permission is distinct from capability.** The CLI plans and selectively creates advice/configuration files; never grants an LLM, IDE or plugin permission to edit code. Installation itself writes to the caller repo and must be locally owner-authorized, even if a plan token matches.

- **Existing root authority:** AGENTS/CLAUDE/GEMINI/Cursor/Antigravity/nested and home rules remain higher-authority. Tool does not parse their semantic requirements. If host law prohibits writing even new adapter files, do not apply.
- **Untrusted source:** No upstream skills or remote setup code are fetched or executed; no `npm install`, postinstall, Git hooks, shell scripting from project, or network operations. Root project package.json is bounded-read and JSON-decoded only.
- **No destructive overwrite:** Managed new paths use exclusive create; collisions fail. Existing root AGENTS/GEMINI can be appended only in explicit opt-in mode, after digest-locked review. Tool refuses symlinked paths and oversized policy files.
- **Rollback protection:** Rechecks exact hashes, refuses rollback if any managed file changes. Doesn't automatically clean directories after rollback; cleanup remains optional. Root marker reversibility assumes no concurrent writer; there is no OS-level sandbox or lock against adversarial local races, and a forced interruption may leave a partial update. Check `verify` and inspect git status on errors.
- **Source coverage:** Top-level framework signals and allowlisted root policies only; nested project sources/global IDE policy not semantically reviewed; no private paths or secrets copied into the ProjectDNA.
- **Security boundary:** Stored SHA-256 receipts detect accidental drift, not malicious actors with the power to rewrite receipts. They are not cryptographic signatures or witness attestations.
- **Host activation:** Code-side file placement may be recognized only after IDE restart/reload and may be ignored according to version/settings. Cloud setup is manual.
- **Releases:** No provenance is inherited from an FDF source-only green CI run. Real host acceptance, browser/keyboard/a11y checks, independent code review, protected branch rules and explicit deployment are separate gates.

## Application vs. evidence

The `plan_sha256` binds the project root fingerprint, bounded policy hash snapshots, targets, platforms and root-hook selection. It is an **operator consent token to a specific local plan**, not a guarantee of user identity, system integrity or intended semantic edits.

## Continuous evolution (v0.1)

Use `inspect` and `plan` when a project evolves. If a managed file already exists, the current v0.1 installer treats a second install as HOLD; do **not** overwrite it. Evolve through human-reviewed repo-native diffs and update the manifest under a future, separately qualified schema. This intentionally prioritizes correctness over automatic self-modification.
