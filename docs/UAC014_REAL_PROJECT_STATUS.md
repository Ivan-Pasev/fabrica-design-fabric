# FDF/UAC-014 — Privacy-minimized owner-project status and real host gate

Date: **2026-11-23**. Original first-party implementation staged on the existing UAC-012/013 **DRAFT PR #16** review branch. No merge, external install or owner project write authorized.

## Why this exists
The existing UAC-010 `fdf_projectdna.py witness` deliberately prints project basename, nested policy filenames and their hashes, and Git HEAD. These can disclose sensitive information if pasted into a chat, repository issue, Drive document or agent context. Its function is still useful for **local private evidence**, but the first operator action should be safe to inspect and share only after a privacy review.

`tools/fdf_owner_status.py` adds a default, **minimized read-only summary**. It internally invokes the opt-in UAC-010 witness within the trusted caller environment, then outputs only coarse policy counts/states, known framework markers, Git clean/dirty status, and the names of `fdf-*` SKILL.md files found in a bounded set of common project skill directories. It omits raw policy text, exact policy paths/hashes, absolute project path, Git commit, project basename and detailed source-fit data.

**Strict claim boundary:** an on-disk `SKILL.md` candidate is neither authenticated first-party source nor a verified native host discovery or activation event. A human operator must inspect actual IDE skills/settings and model invocation separately. Global, team and effective nested policy precedence remains UNKNOWN. Output does not authenticate owner consent. No skill or code installation occurs.

## One-command read-only owner pilot

Run from a pinned FDF draft checkout **outside** the actual project and under the project's own host rules:

```powershell
py -3.12 tools\fdf_owner_status.py status --project "C:\path\to\your-existing-project" --host antigravity --intent design
```

On Linux/macOS, substitute `python3` and the real project path. The `--host` argument is a declaration, not host identity verification. Supported intents: design, motion, spatial, quality, mobile, tokens, runtime, components.

The command prints JSON to stdout; **no project file is intentionally written**. It invokes Git read-only status commands through the existing UAC-010 witness, and file-inventory reads only metadata and policy bytes for internal hashing; it does not print those bytes. Do not redirect into a public log. Review output for disclosure before copying it to connected systems.

Next, manually inspect the active IDE's actual skill list: if no first-party FDF skill is loaded, return `HOST_SKILL_NOT_OBSERVED` and **do not install automatically**. If present, observe real activation, collect redacted owner evidence privately, compare before/after project status, and run `fdf_host_evidence.py review` only after the real UAC-010 private witness and UAC-011 observation exist. That reviewer checks consistency but cannot authenticate the IDE.

## Exact source checks and limitations

The GitHub workflow runs 14 source-only tests on Ubuntu and Windows (one symlink test skips where Windows privilege is unavailable) and executes the read-only minimized status against the checked-out **actual FDF GitHub repository**. This last check is a real source-tree probe in CI, **not** an owner's local IDE witness. The existing repo-wide test suite runs independently.

The script does not guarantee safety against hostile concurrent filesystem writes, Windows reparse/junction attacks, untrusted Git binaries/configuration, very large nested workspaces, uninspected global host policies, or commands outside the scoped script. FDF does not currently hold evidence that an owner IDE loaded a named skill. Source SHA, metadata hashes and user-filled JSON flags are not cryptographic owner signatures.

**NEXT admission gate:** actual redacted owner-controlled ProjectDNA and host-native skill discovery/activation observation from **one real project**. Require independent review before any source promotion, installation, approval, merge or release. Preserve earlier FDF source provenance and copyright boundaries.
