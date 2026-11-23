# FDF/UAC-013 — One-project real IDE admission quickstart

**Status: OWNER_HOST_EVIDENCE_PENDING.** This is an owner-operated, non-installing pilot. It is not a release instruction. The reviewed GitHub branch is [draft PR #16](https://github.com/Ivan-Pasev/fabrica-design-fabric/pull/16).

## 1. Start in the actual owner IDE

Choose **one existing project** opened in the actual host (Antigravity, Cursor, Codex or Gemini CLI). Confirm it is the intended project, note Git HEAD/status and effective team/global/project/nested instructions through host-native controls. Existing instructions prevail; FDF is a lower-priority design/intelligence reference.

Use a separate local checkout of the FDF draft PR source. **Do not copy FDF source files into the caller project for this read-only pilot.**

## 2. Read-only ProjectDNA (operator-controlled command)

```shell
python tools/fdf_projectdna.py witness --project "/absolute/path/to/real-project" --host antigravity --intent design
```

The tool prints JSON. Save it in a private location **outside the caller repository** only through an explicit owner shell action; it does not create files itself. The host flag is merely self-declared, and results may include sensitive project names, relative policy paths and file hashes. Do not publish the raw witness.

## 3. Independently observe discovery and activation

Inspect the real host's skill directory/list and current project instruction precedence. If the chosen FDF first-party skill is not found, record this as **NOT_DISCOVERED**, do not install it silently, and stop at the required owner approval gate. If it is discovered and genuinely activated, observe the native host UI/CLI signal. Ask for one **read-only** project-specific ProposalDNA, and compare it with actual existing code and project law.

The model's statement that a skill was loaded does not constitute independent evidence. GitHub CI is only source-level evidence.

## 4. Record a deliberately incomplete starting observation

Copy `examples/UAC013_OWNER_OBSERVATION_TEMPLATE.json` to a **private owner-controlled location** and edit it only after actual operator observation. Replace the placeholder ProjectDNA hash, verified FDF source commit, and correct host. Leave unverified flags FALSE, including independent review PENDING. DO NOT upload private evidence, host screenshots or policy text into a public PR.

## 5. Triage consistency, not authenticity

```shell
python tools/fdf_host_evidence.py review --projectdna "/private/projectdna.json" --observation "/private/observation.json"
```

The tool verifies local evidence schema/digest consistency and missing fields, but cannot independently authenticate an owner or skill activation. Even a complete self-report yields `EVIDENCE_INTAKE_REVIEW_REQUIRED`, never PASS/INSTALL/MERGE/RELEASE.

## Admission closure

Requires real operator observation, independent source/effect review, actual host capability and instruction scope, unchanged Git status (or owner-approved reversible change), separate owner decision and independent human code/release review. **Current live IDE qualification remains HOLD**. Windows junction/reparse and concurrent filesystem hardening remain unresolved. The prior October UAC-012 ZIP was not mounted in the 2026-11-23 build environment; use the current reviewed Git source instead.
