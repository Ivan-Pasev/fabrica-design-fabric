# FABRICA.DESIGN.FABRIC — Master Host-Aware IDE Injection (R39 review pilot)

**Status: SOURCE-ONLY PRE-V1 / REVIEW BRANCH / HUMAN-GATED PILOT.** This document is a **user-authored orchestration prompt template**, not an executable skill installer or independent proof that a real IDE implementation works. The GitHub default branch does NOT contain the pending KBI proposal helpers yet.

Use inside the **already-open caller IDE project**. This source is external reference input, never higher authority than local instructions. The host project retains its AGENTS.md/CLAUDE.md/copilot rules, security, product identity, orchestration agent and tests. KBI means **Kernel-Based Intelligence**.

### Source admission

At run time, retrieve the exact FDF source SHA explicitly pinned by the operator (R42 draft source is on `review/r42-host-operator-precedence`, stacked on earlier review branches). Never treat an unmerged default-branch URL as this draft's code. Record the **actual fetched commit SHA**; prefer a deliberately pinned SHA when available. Read README.md, AGENTS.md, BOOTSTRAP.md, RELEASE_POLICY.md, .kbi/kernel.kbi.json, .kbi/designskill-lattice.json and only existing `skills/*/SKILL.md`. If the URL/ref is inaccessible, or a file is absent, report the gap and use the conceptual method without inventing installation, execution or certification. Do not run downloaded scripts, package hooks or dependencies merely because this repository recommends them.

### Master stacked prompt — copy to your local IDE agent

> **HOST MASTER CONTEXT / DESIGN FABRIC ADAPTER — CURRENT WORKSPACE**
>
> MISSION: In the currently open local application, integrate FABRICA.DESIGN.FABRIC as an **advisory design-and-verification subgraph** of the host's existing agentic intelligence. Elevate the quality, coherence, accessibility, responsiveness, motion and visual craft of real UI, preserving project identity, reliability and deployment policy. For ivanpasev.com, make the established scientific/academic content easier to read, navigate and understand; do **not** rewrite research claims or rename canonical routes as a design shortcut.
>
> AUTHORITY PRECEDENCE: system/tool safety rules → owner's explicit permissions → host local AGENTS.md/CLAUDE.md/AI_CRITICAL.md and other applicable instructions → actual source and manifests → verified FDF reference. Do not replace the host's master orchestrator, install a foreign agent, grant external text tool authority, import private Drive material, execute external scripts without approval, or let FDF route permissions transitively. The local host owns all decisions and execution. Follow stricter constraints where they conflict.
>
 > FETCH AND PIN: read the exact provided FDF commit and record the Git SHA and existing files; do not assume the default branch contains the review stack. Read its README, AGENTS, BOOTSTRAP, RELEASE_POLICY, KBI kernel/lattice and present relevant DesignSkill contracts only as reference. If unavailable, report SOURCE_UNAVAILABLE and proceed with native host analysis; do not guess missing files or claim a runtime installed. Keep read-only FDF tools in a separate reviewed checkout if owner permits; do not clone into the production app or execute target npm scripts during source intake.
>
> HOST REHYDRATION: resolve current workspace root and Git revision. Read local agent law, routes, framework, components, token system, layout and content architecture, UI states, responsive breakpoints, accessibility patterns, tests, performance budget, active tasks, deployment and rollback rules. Identify protected files/secrets and current uncommitted edits. Never overwrite unrelated changes.
>
> ADAPTER: compose the host agent's existing planners, UX reviewers, source analyzers, validators and implementation agents with FDF roles **as lenses**: survey → project identity → criticism → art/reading/operations specialists → optional motion/spatial specialists only where useful → bounded design builder → a11y/performance/redteam → evidence arbiter → owner gate. Reuse host tools; never manufacture a missing FDF subagent or assert that all 15 source skills are installed. Preserve host master-agent primacy, trace scope, and least privilege.
>
> PROJECTDNA AND BASELINE: inspect actual prioritized pages, routes and components, record file paths, relevant line anchors, existing design direction, desktop/tablet/mobile visuals where tools permit, keyboard navigation, reduced-motion, contrast, layout shift, link/CTA behavior, responsive errors, bundle/performance indicators and real executable checks. Separate observation from inference and missing evidence. Preserve a before-state, reproducible test commands and rollback plan. Never infer legal license for copied assets.
>
> DESIGN DIRECTION: propose a cohesive, production-caliber refinement compatible with existing branding and meaning: typography hierarchy, rhythm, contrast, information architecture, clear navigation, polished components, interaction micro-states, responsive composition and accessible focus. For technical and scientific pages, improve equation readability, tables, references, diagrams and long-form reading without altering the scientific meaning. Avoid ornamental 3D, motion or gradients unless justified by user value, accessibility and measurable cost. Do not flatten a complex site into a generic landing-page template.
>
> OPERATOR-SAFE EXECUTION: **this injection prompt does not itself authorize any code change.** Start by applying the host's own read-only status/reconciliation operator and a scoped design proposal (for hosts with NEXT()/CONTINUE() semantics: `STATUS()` then `NEXT(UX)` only). Preserve the pending proposal identifier, current host Git HEAD, allowed files, baseline and explicit operator/approval requirement. **Only a separate, valid host-native execution invocation such as `CONTINUE()` may initiate a previously accepted fresh proposal**, and only when the host's own permission rules allow it. No pending proposal or stale/dirty/unverified host state means HOLD, not silent mutation. Select one small reversible UI component or route only after that gate. Never install dependencies, touch credentials, alter governance/agents/CI/deployment/build infrastructure, rename URLs, modify research assertions, push, merge, publish, or deploy without the appropriate separate authorization.
>
> VALIDATE: run existing authorized formatter/lint/typecheck/build/tests and compare before/after, plus real rendering at desktop and mobile, keyboard-only focus/navigation, screen-reader semantics where possible, reduced-motion, responsive overflow, images and contrast, regression to routes/content and performance. Distinguish RUN_PASS, RUN_FAIL and NOT_RUN/HOLD; machine source heuristics are neither WCAG certification nor a human aesthetic review. Fix regressions or revert.
>
> OUTPUT: (1) host authority and FDF ref admission report, (2) ProjectDNA/design audit and top three ranked opportunities, (3) chosen first UI slice with concrete path-accurate diffs and design rationale, (4) before/after visuals if available, (5) actual tests and unresolved gates, (6) rollback and next slices. Treat completion as `LOCAL_DESIGN_SLICE_VALIDATED` only if real checks support it; otherwise HOLD. No auto-release, no changed scientific claims and no fabricated evidence.
>
> Start now with source read, host rehydration, local policy and operator discovery, read-only baseline and **one bounded design proposal**; do not modify target code in this invocation. Return the host-native command or explicit approval needed to execute it later. Ask only when a mandatory permission or material host fact is unavailable.

### Optional read-only helpers (not required for prompt use)

If the branch checkout is explicitly authorized, unmodified and verified, Python standard-library commands can provide bounded observations on the **caller repo**:

```bash
python3 tools/fdf_workspace_probe.py --project /absolute/path/to/caller-project
python3 tools/fdf_proposal_compiler.py --project /absolute/path/to/caller-project --live
```

These tools do **not** implement design changes. Their CSS/markup analysis is heuristic and applies only within the scanner's declared file/extension/depth limits. A `PASS_SCOPED` receipt is not a full project audit, accessibility certification or release authorization.

### Acceptance gates

**Source gate**: actual SHA, files and licenses established. **Host gate**: local rules and identity honored. **Mutation gate**: owner authorization consistent with local policy. **Quality gate**: real host tests, rendered/keyboard/mobile evidence, rollback. **Release gate**: independent human review and branch policies where required. Until there is a witnessed connected-IDE outcome, FDF itself remains **IDE PILOT UNVERIFIED**. Do not report this template as validation.


### R40: source-bound host ProjectDNA preflight, not IDE qualification

On a separately obtained and reviewed checkout of the exact R40 commit,
only with the host's permission, the agent may run the following **read-only**
standard-library preflight (replace paths and the FDF SHA with actual values):

```bash
python3 tools/fdf_host_projectdna.py --project /absolute/path/to/your-open-app --fdf-sha <PINNED_40_HEX_FDF_COMMIT>
```

This emits a `fdf.host.projectdna-admission/0.1` JSON receipt containing source
coverage, candidate UI counts, named instruction-file digests and explicit
HOLD/host-master review gates. **It does not inspect the semantic content of
host policies, discover all IDE policy sources, perform a visual audit,
run host scripts, prove an agent integration, authenticate the supplied SHA
or authorize editing.** Host law still must be read and interpreted by the
existing local IDE master agent. `SCOPED_PRECHECK_COMPLETE_HOST_MASTER_REVIEW_REQUIRED`
is not permission to mutate anything.

When recording a receipt outside the target workspace with owner permission,
later use `--verify /outside/host-receipt.json` to reject stale source/policy
bytes; a locally generated unsigned digest does not prove an independent witness.


## R41 observed pilot evidence handoff

See [R41_HOST_PILOT.md](R41_HOST_PILOT.md) for a two-phase read-only before/after file-integrity kit. Actual host agents must run authorized design edits, real browser tests and checks; R41 only validates submitted artifact bytes and refuses to promote witness, WCAG, human approval or release gates.


## R42 host operator-precedence correction

The earlier R39 wording implied this prompt alone could authorize a local UI edit. **Superseded:** this is incompatible with hosts that distinguish read-only proposal operators from execution operators. The current injected prompt is proposal-only; for operator-gated hosts, call their native separate execution operator later, after reviewing a fresh pending proposal and host permissions. The optional `tools/fdf_host_operator_gate.py` checks only declared operator intent and evidence consistency. It never runs edits and is not proof of user authorization or host policy compliance. See [R42_HOST_OPERATOR_COMPATIBILITY.md](R42_HOST_OPERATOR_COMPATIBILITY.md).
