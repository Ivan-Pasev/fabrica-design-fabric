# FDF/UAC-014 — Privacy-minimized owner-project status and real host gate

Date: **2026-11-23**. Original first-party implementation staged on the existing UAC-012/013 **DRAFT PR #16** review branch. No merge, external install or owner project write authorized.

## Why this exists
The existing UAC-010 `fdf_projectdna.py witness` deliberately prints project basename, nested policy filenames and their hashes, and Git HEAD. These can disclose sensitive information if pasted into a chat, repository issue, Drive document or agent context. Its function is still useful for **local private evidence**, but the first operator action should be safe to inspect and share only after a privacy review.

`tools/fdf_owner_status.py` adds a default, **minimized read-only summary**. It now uses a **separate bounded metadata-only observer** instead of invoking the UAC-010 content-hashing witness. It reports coarse policy-file counts/states, known framework markers, **Git state UNKNOWN (Git is not invoked)**, and the names of `fdf-*` SKILL.md file candidates found in common project skill directories. It omits raw policy text, exact policy paths/hashes, absolute project path, Git commit, project basename and detailed source-fit data.

**Strict claim boundary:** an on-disk `SKILL.md` candidate is neither authenticated first-party source nor a verified native host discovery or activation event. A human operator must inspect actual IDE skills/settings and model invocation separately. Global, team and effective nested policy precedence remains UNKNOWN. Output does not authenticate owner consent. No skill or code installation occurs.

## One-command read-only owner pilot

Run from a pinned FDF draft checkout **outside** the actual project and under the project's own host rules:

```powershell
py -3.12 tools\fdf_owner_status.py status --project "C:\path\to\your-existing-project" --host antigravity --intent design
```

On Linux/macOS, substitute `python3` and the real project path. The `--host` argument is a declaration, not host identity verification. Supported intents: design, motion, spatial, quality, mobile, tokens, runtime, components.

The command prints JSON to stdout; **no project file is intentionally written**. The status command deliberately **does not open/read policy contents, compute policy-file hashes, query the Git CLI or fetch remote registries**. It uses bounded `os.scandir` directory traversal and ordinary metadata/stat checks. For full forensic evidence (policy hashes, Git SHA), run the separate UAC-010 witness only with explicit local authorization and keep its more sensitive output private. Do not redirect into a public log. Review output for disclosure before copying it to connected systems.

Next, manually inspect the active IDE's actual skill list: if no first-party FDF skill is loaded, return `HOST_SKILL_NOT_OBSERVED` and **do not install automatically**. If present, observe real activation, collect redacted owner evidence privately, compare before/after project status, and run `fdf_host_evidence.py review` only after the real UAC-010 private witness and UAC-011 observation exist. That reviewer checks consistency but cannot authenticate the IDE.

## Exact source checks and limitations

The GitHub workflow runs 22 source-only tests on Ubuntu and Windows (two symlink tests skip where Windows privileges are unavailable) and executes the read-only minimized status against the checked-out **actual FDF GitHub repository**. This last check is a real source-tree probe in CI, **not** an owner's local IDE witness. The existing repo-wide test suite runs independently.

The minimal status script does not guarantee safety against hostile concurrent filesystem writes, Windows reparse/junction attacks, very large nested workspaces, uninspected global host policies, or commands outside its narrow scope. **Git binaries/configuration are no longer exercised by the basic status command**, but the optional full UAC-010 witness still uses them. FDF does not currently hold evidence that an owner IDE loaded a named skill. Source SHA, metadata hashes and user-filled JSON flags are not cryptographic owner signatures.

**NEXT admission gate:** actual redacted owner-controlled ProjectDNA and host-native skill discovery/activation observation from **one real project**. Require independent review before any source promotion, installation, approval, merge or release. Preserve earlier FDF source provenance and copyright boundaries.

## UAC-015 stricter privacy invariant (23 November 2026)

The basic `status` path now has **zero policy-file content reads, zero hashes, and zero Git subprocesses** by design; it does not obtain a complete Git clean/dirty witness. New unit tests explicitly fail if a content reader, original UAC-010 witness, or subprocess is used. Count/inventory limits and symlink/junction detection fail to HOLD. This is a **lower-access status probe**, not an expansion of actual native IDE observation. All human, release and host-skill activation gates remain HOLD.
