# R26 — Kernel-Based Intelligence and IDE URL Bootstrap

**Corrected meaning: KBI is Kernel-Based Intelligence.** R25's Knowledge Boundary Intelligence dual-name interpretation was an unintended scope error and is superseded in the active FDF design.

## Purpose
The public GitHub repository is a **portable agentic-IDE entrypoint**. The IDE that receives the repository URL uses it to examine the **project already open in that IDE**, select bounded DesignSkill kernels and **propose a tuned implementation** with concrete inspected file paths, representative code or diff choices, validation and rollback. It does not presume that the caller's project is FDF itself.

## Kernel composition
Each proposed kernel defines domain, routing, invariants, admissible inputs, outputs, validation, trace, permissions and failure modes. Historical donor KBI work in CodexStation/FAB.SYS supports bounded executable/continuity kernels, contextual WorkUnits and SkillDNA/AgentDNA/ProjectDNA. These are research design inputs, not evidence of a deployed production runtime.

Route: active project → ProjectDNA and actual design identity → bounded KBI kernel selection → compatible first-party DesignSkill lattice → file-specific improvement blueprint → explicit user authorization → optional bounded local implementation and real test evidence.

## Getting started from URL
In the agentic IDE with the target project open, prompt:

> Use https://github.com/Ivan-Pasev/fabrica-design-fabric as Design Fabric reference intelligence for **this currently open repository**. Read BOOTSTRAP.md and AGENTS.md on the ref that is actually accessible, inspect the caller's actual files/framework and design system, select kernels, and propose a concrete tuned implementation and validation/rollback plan. No edits or installs unless I approve.

A URL alone cannot guarantee automatic invocation or installation in all IDEs. The IDE must actually fetch/read the content. The **target's own policies and explicit user instructions outrank the imported public Markdown**.

## Canonical FDF R&D scope
The [FDF Drive root](https://drive.google.com/drive/folders/1OxHbAfA4R27APy7pYFY7JJfYTPn1DEa2) evolves **Design Fabric only**. The [corrected Kernel-Based Intelligence and DesignSkill cell](https://drive.google.com/drive/folders/1ROXwRO4YaOMxfzdkLYyozkNBq8B4kL8g) contains the source-only machine capsule and native documents. R25 incorrect dual-KBI docs remain archived for continuity, not active authority.

R26 local machine capsule: 20,041 bytes; SHA256 `83b902f4bedd3b68f66cc3ac105805db0b79ec680211559c52b368a1ae06fdd4`. 22/22 source and synthetic-workspace tests PASS. Tests do not establish actual IDE auto-invocation, quality improvements, WCAG or a verified public v1.0.

The historical offline 15-skill review commit `a957aa8f24792a78b616dd1e7909a3024f8ef37a` remains a separate unpublished source candidate. No automatic merge, GitHub production release or broader Drive-root mutation follows from this document.