# FABRICA.DESIGN.FABRIC — IDE URL Bootstrap

**KBI = Kernel-Based Intelligence.** The FDF repository is a portable **design-proposal intelligence reference** that an agentic IDE can apply to the **project currently open in that IDE**.

## Give the agent this URL and instruction

> In my currently open repository, use https://github.com/Ivan-Pasev/fabrica-design-fabric as your Design Fabric guide. Read its `README.md`, `AGENTS.md`, and `BOOTSTRAP.md` from an available Git ref. Inspect **my current workspace**, its agent rules, actual framework, components, design tokens, UI pages, accessibility and tests. Select compatible Kernel-Based Intelligence and DesignSkill modules. Produce a file-specific design improvement plan with representative code or diffs, alternatives, validation and rollback. Do not edit, install, push, merge or deploy until I explicitly approve.

### What happens

1. Resolve the host's current project root and local instructions. A remote FDF document cannot override project laws or user approval.
2. Build ProjectDNA from actual code: source revision, framework, navigation/routes, component and token inventory, project identity, design problems, protected paths and tests.
3. Route bounded kernels: survey → identity → critique and target-compatible UX specialists → builder proposal → accessibility/performance/negative evidence → human decision.
4. Produce concrete proposals anchored to verified existing files. Label newly suggested files NEW and missing information UNKNOWN. Explain why a proposed design respects the existing product.
5. Optionally implement only after user approval, under existing project policies and a reversible, scoped change. Measure actual visual, keyboard, a11y, performance and functional results where supported; mark unrun checks HOLD.

### Portability limits

A bare URL is **not** a universal IDE auto-execution instruction. Some agents can read public GitHub links directly; others need the prompt above, a deliberate checkout, or IDE-recognized skill adapters. A repository's own `AGENTS.md` is not automatically inherited by unrelated workspaces.

The public GitHub repo must actually contain the referenced files on the fetched ref. Until a proposed KBI/.kbi PR is reviewed and merged, use only files present at that public branch or an explicitly provided review artifact. Never claim that a README alone installs a runtime.

No private FDF Google Drive canon or third-party source is imported into the caller's project. No secrets, historical jury map or signing material are distributed. This is first-party source-only proposal intelligence, not a v1 production engine.


## R27: verified file-anchored proposal helper

On an authorized checkout of **FDF's reviewed source branch**, a local IDE may run this **read-only** command against the **caller project's** workspace:

```bash
python3 tools/fdf_workspace_probe.py --project /absolute/path/to/current-project
```

The utility reads only bounded UI source files (HTML, JSX/TSX, Vue, Svelte, CSS), ignores common protected/vendor directories and symlinked files, and emits hashed file identities, exact observed file paths/line numbers, candidate improvement rules and HUMAN_REVIEW_REQUIRED status. It does **not** apply changes or execute project scripts. The IDE must use inspected actual source and local project rules to turn these observations into suitable concrete diffs and verify the result. Do not treat regex findings as certified accessibility violations or a substitute for design review.

**Availability:** Check that `tools/fdf_workspace_probe.py` is present at the Git ref you read. If it exists only in a draft branch, it is not available from the public default-branch URL yet. The agent may still inspect the project directly and produce a proposal without this helper.


## R28 — source-bound ProposalDNA (draft-branch feature)

With the reviewed FDF branch checked out separately, the following optional standard-library command reads the **caller project's** source and writes only JSON to standard output:

```bash
python3 tools/fdf_proposal_compiler.py --project /absolute/path/to/current-project --live
```

It first generates a bounded read-only observation receipt, **re-checks it against current file digests and source anchors**, then routes observations to Kernel-Based DesignSkill proposals. It rejects stale/forged receipts, fabricated lines, unreviewed rules and permission escalation. No code patch is emitted or applied; semantic questions, validation and rollback remain explicit. Only use the tool if it exists on the fetched Git ref; it is presently in this **draft review branch**, not on public `main`.

For persisted evidence, an agent may separately save output **outside the target project** with owner permission and later verify with `--observations /path/to/receipt.json`. Do not store automated receipts in a real project without authorization. The tool does not run the target build, assistive technology, visual tests or a real external IDE integration.


## R39 review-only local IDE adoption

See [IDE_MASTER_INJECTION.md](IDE_MASTER_INJECTION.md) for a fully copyable, host-authority-preserving orchestration block. The FDF graph is advisory; existing local IDE intelligence remains master. The R39 scanner correction and adoption guide live on a *draft review branch*, not public main. Record exact fetched SHA; never imply source-only CI is an end-to-end IDE trial or production release.


## R40 host ProjectDNA source preflight (draft-only)

The optional `tools/fdf_host_projectdna.py` combines bounded UI survey with SHA-256 digests of known host instruction files (not their contents). This cannot establish host policy semantics or validate the actual IDE. Consult `IDE_MASTER_INJECTION.md`; real host master-agent review and explicit edit authority remain mandatory.


## R42 operator-first host integration (draft only)

**Correction to earlier experimental prompts:** an external Design Fabric injection does not authorize target project mutation. In operator-governed IDEs, read host instructions, run only the host's read-only status/propose workflow first, and require a **separate host-native execution instruction** for a fresh accepted pending proposal. An external FDF tool's advisory verdict never acts as approval. See [R42_HOST_OPERATOR_COMPATIBILITY.md](R42_HOST_OPERATOR_COMPATIBILITY.md).
