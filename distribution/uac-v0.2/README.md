# FABRICA.DESIGN.FABRIC — FDF() Universal Adoption 0.2

**One injection → source-grounded ProjectDNA → fit-ranked first-party skills → additive root intelligence → owner-authorized install → versioned guided evolution.**

## Start in any active coding IDE

Open `FDF_UNIVERSAL_INJECTION.md` and paste its entire content into the project's **existing** agent chat. It does not automatically install anything; it requests discovery and a reviewable plan. Install this package **outside** the project you are adopting.

For a real terminal in the owner's workspace:

```sh
python tools/fdf.py FDF --project /path/to/existing-project --platforms codex,cursor,antigravity,gemini,chatgpt,aistudio
# Output: observed ProjectDNA, selected first-party skills, collision report, plan_sha256.
# Review the plan, local host/global/nested rules, skills and diffs before changing any files.
python tools/fdf.py apply --project /path/to/existing-project --platforms codex,cursor,antigravity,gemini,chatgpt,aistudio --approve-plan <exact-plan_sha256>
python tools/fdf.py verify --project /path/to/existing-project
python tools/fdf.py evolve --project /path/to/existing-project
# Guarded rollback of exactly the approved installation:
python tools/fdf.py rollback --project /path/to/existing-project --approve-plan <same-plan_sha256>
```

For an explicit root AGENTS/GEMINI pointer, request `--root-hooks append` **during both plan and apply**, with a new SHA. The default never modifies those files. Rollback refuses to remove files subsequently edited by the caller.

## Platform selection

- **Codex / OpenAI models:** `AGENTS.md` governed by existing local law; optional first-party skills in `.agents/skills`. No global install.
- **Cursor:** `.cursor/rules/fabrica-design-fabric.mdc` uses optional agent-requested context, plus existing rules preserved.
- **Google Antigravity IDE/CLI:** `.agents/rules/*.md` with valid `trigger: model_decision`, workspace `.agents/skills`; no new legacy workflows. Vendor's announced cutoff for old `.agents/workflows` is October 19, 2026.
- **Gemini CLI:** `.gemini/skills` and an optional minimal `GEMINI.md` bridge. Skills may require host reload/activation.
- **ChatGPT Projects:** use generated copyable manual project instructions and attach permitted project sources; local files cannot reconfigure cloud Projects.
- **Google AI Studio Build:** import an authorized GitHub project, use generated manual Build prompt, review all edits and GitHub sync; no assumption that `.agents/skills` is auto-loaded in AI Studio.

## Skill lattice

A static project-signal selector builds `.fabrica/SKILL_LATTICE.json` and installs the selected original **first-party** skills only for verified platform types. Universal: Project Observer, Governance Gate, Evolution Planner, Verification Engine. Conditional: Design Critic, Accessibility Review, Motion Director, Runtime Architect, Research Provenance. Unselected skill bodies are not installed. `emilkowalski/skills` is explicitly pinned as a lower-trust MIT upstream **reference** and never downloaded or vendored automatically.

An existing root orchestration surface triggers advisory **augment**. If none is detected, FDF scaffolds `.fabrica/KERNEL.md`, `EVOLUTION_POLICY.md`, `STATE_AND_HANDOFF.md`, `PROPOSAL_TEMPLATE.md`; this is not a declaration that global policies are absent and is not a privileged self-modifying kernel.

## Safety and evidence

- `FDF()` only observes/plans; `apply` requires a reviewed digest. A SHA verifies exact plan consistency, **not owner identity**.
- Static source signals do not prove framework semantics, model behavior, policy compliance, actual IDE activation, visual quality or business permission.
- No external installs, network fetch, code edits, Cloud pushes, Git merges, API key changes or deployment are performed by this utility.
- Existing policies, identity, files, designs, active tasks and precedence remain authoritative. The generated prompts preserve host law.
- This utility is not a security sandbox or TOCTOU-complete transaction manager. Never apply to high-risk/untrusted/symlinked workspaces without independent code review.
- Current version supports additive new installs. For later releases, explicitly review a versioned migration; current managed-file collisions HOLD rather than overwriting.

## Tests

`python -m unittest discover -s tests -v`

Local controlled fixtures test new project, mature project, cloud/manual adapters, suite integrity and rollback. They are **not** real authenticated Codex, Cursor, Antigravity, Gemini CLI, ChatGPT or AI Studio sessions.

## Repository and canonical R&D

FDF review stack: https://github.com/Ivan-Pasev/fabrica-design-fabric ; R&D root https://drive.google.com/drive/folders/1OxHbAfA4R27APy7pYFY7JJfYTPn1DEa2 ; universal adoption issue https://github.com/Ivan-Pasev/fabrica-design-fabric/issues/11. Do not claim external human review, protected-main governance or release completion from source-only tests.
