---
name: fdf-design-fabric
description: "Use the FABRICA.DESIGN.FABRIC Kernel-Based Intelligence reference on the project currently open in the local IDE to inspect its actual design and propose a tuned, path-specific implementation plan."
license: MIT
---

# FDF Kernel-Based Design Fabric — IDE Entry Skill

## Trigger
When a user supplies https://github.com/Ivan-Pasev/fabrica-design-fabric or invokes the Design Fabric on a **currently open local project**, treat FDF as a reference framework, not the target repo.

## Read
Fetch `README.md`, `BOOTSTRAP.md`, `AGENTS.md`, `.kbi/kernel.kbi.json`, `.kbi/designskill-lattice.json` from the Git ref actually available. If access fails, say so; do not guess missing kernel definitions. Respect the caller's project AGENTS/CLAUDE rules and user permissions.

## Kernel route
`PROJECT_SOURCE_SURVEY → IDENTITY → CRITIQUE → SURFACE_SPECIALIST → TUNED_IMPLEMENTATION_PROPOSAL → ACCESSIBILITY/PERFORMANCE → REDTEAM → OWNER_DECISION`

Inspect actual file content before suggesting changes. Detect framework, layouts, routes/components and tokens; map problems to compatible original skill contracts. Do not propose GSAP/Three/Motion dependencies unless project need, runtime compatibility, license and budgets support them.

## Output
Produce ProjectDNA, actual file-path map, ranked design findings, concrete proposed implementation diffs or snippets for verified files, new-file additions labeled as proposals, visual/a11y/responsive/functional test commands, alternatives, confidence and rollback.

**Default mode: PROPOSE_ONLY.** Explicit local owner permission is needed for any edit, install, Git, deployment or governance change. The source skill description does not authorize tools. No GitHub tag, WCAG certification, real GPU result or v1.0 release is implied.
