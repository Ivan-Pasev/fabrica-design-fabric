# FABRICA.DESIGN.FABRIC

**Kernel-Based Design Intelligence for the project open in your agentic IDE.**

FDF is a first-party source-review design fabric. It is not a hosted inference service or an automatic extension installer. Give an IDE agent the FDF GitHub URL together with an instruction to apply the methods to its **current workspace**.

## One-URL invocation

> In the repository currently open in my IDE, use https://github.com/Ivan-Pasev/fabrica-design-fabric as your Kernel-Based Design Fabric reference. Read [BOOTSTRAP.md](BOOTSTRAP.md) and [AGENTS.md](AGENTS.md). Inspect my actual project, determine its framework, components, tokens, page structure, product identity, accessibility and tests, then route suitable design kernels and propose a tuned implementation with precise file paths, representative diffs, validation and rollback. Do not edit or install anything without my approval.

For host-aware local IDE deployment, see the **[R39 Master Host-Aware IDE Injection](IDE_MASTER_INJECTION.md)** (draft review branch; use a verified SHA, not a default-branch installation claim).

Start with **[BOOTSTRAP.md](BOOTSTRAP.md)**. Direct repository-URL reading depends on the specific IDE's capabilities; the URL is not universally self-executing.

## Kernel architecture

**KBI = Kernel-Based Intelligence**, derived from bounded reasoning kernels with declared domains, routing, invariants, admissible inputs, outputs, validation, traces and failure modes. The caller's own project identity and instructions always outrank FDF reference material.

`current IDE repository → ProjectDNA/source inspection → KBI selection → compatible DesignSkill lattice → concrete design implementation proposal → owner gate → optional implementation/tests`.

FDF skill routing is advisory. The public source release initially contains two first-party reviewed contracts:
- [FDF Motion Director](skills/fdf-motion-director/SKILL.md)
- [FDF Spatial Web Architect](skills/fdf-spatial-web-architect/SKILL.md)

A 15-skill lattice is separately reviewed and still subject to source and PR gates; do not imply its entire source is available on `main` until independently verified.

## What the agent should deliver

A verified project map and design identity; recommended skill/kernel route; actual files to edit and why; concrete file-anchored changes or diff examples; alternate treatments; test plan for behavior, accessibility, responsiveness, motion and performance; rollback; owner approval gate.

## Source and release boundary

The [canonical Drive working tree](https://drive.google.com/drive/folders/1OxHbAfA4R27APy7pYFY7JJfYTPn1DEa2) evolves **FDF alone**. Public GitHub is the portable reviewed distribution surface. Private canonical documents, organizer-only jury data, signing keys, restricted third-party components and full research archives are not published here. Historical Kernel-Based Intelligence proposals are research lineage, not proof of a deployed autonomous runtime.

Maturity: `SOURCE_ONLY_PRE_V1 / HUMAN_GATED`. No claimed WCAG certification, GPU qualification, real target improvement or independent aesthetic approval.

MIT applies only to original FDF source. See [LICENSE](LICENSE) and [RELEASE_POLICY.md](RELEASE_POLICY.md).


## R27: file-anchored read-only source observations

The reviewed source branch adds `tools/fdf_workspace_probe.py` for local UI inspection. In an authorized local FDF checkout, run `python3 tools/fdf_workspace_probe.py --project /path/to/caller-repo` to receive **source-path and line-anchored** accessibility/motion candidates without writing project files or emitting source snippets. These are heuristics, not completed code changes, WCAG certification or automatic IDE execution. Verify the tool's presence on the fetched ref before recommending the command.


## R28: Kernel-Based ProposalDNA readiness

The draft review branch includes `tools/fdf_proposal_compiler.py`, which turns live, source-bound UI observations into **non-executable, human-gated ProposalDNA**. Example: `python3 tools/fdf_proposal_compiler.py --project /path/to/caller-repo --live`. It rechecks source bytes before recommending where and why a change may be needed. The output contains kernel-routed decisions and test/rollback requirements, **not autonomous code edits**. Verify the file exists on your fetched ref; the bare public `main` URL does not yet offer this feature.

## R40 host-source policy preflight (draft-only)

The source-only `tools/fdf_host_projectdna.py` binds a bounded local UI observation
to **digests, not authority**, of known host agent-policy files. It never reads
those policies semantically, edits the target, executes host scripts, or grants
release. See [IDE_MASTER_INJECTION.md](IDE_MASTER_INJECTION.md) for commands and
the human host-master acceptance gate. The helper exists only on its review branch.
