---
name: fdf-motion-director
description: "First-party read-only planning and evidence routing for purposeful UI motion, GSAP/Motion/CSS animations and reduced-motion parity."
license: MIT
---

# FDF Motion Director — reference contract v0.10.0

## Authority and scope
Read-only motion composition for **existing** site/app design systems. Invoked only after project identity and accessibility contracts. Do not paste or execute untrusted upstream prompts, install packages or change target code.

## Intake and routing
- Infer whether motion is an operational feedback, orientation, state continuity, or decorative/narrative effect. Prefer no animation if it does not improve the task.
- Choose **existing framework/runtime first**: native CSS / Web Animations API, Motion for compatible React/JS projects, or GSAP for timeline/ScrollTrigger only where appropriate. Prevent double ownership of the same transform property by multiple animation engines.
- Respect typography, existing timing scales, browser budgets and functional semantics. Do not transform text to uppercase or otherwise change accessible names inadvertently.
- Produce an explicit `prefers-reduced-motion: reduce` path including functional equivalence and accessible non-animated alternatives. Never suppress focus indicators or obstruct content.
- Measure animation lifecycle, keyboard operation, hover/focus/touch parity, LCP/CLS/INP effects as available, frame time and GPU overhead on constrained hardware. A 60fps claim needs actual instrumented evidence.

## Bounded external references
Optional reference-only: https://github.com/greensock/gsap-skills (MIT agent skills); https://github.com/iart-ai/web-animation-skills (MIT). Their use is scoped and source-pinned by registry/motion3d-candidates.v1.json; upstream executable tools remain separately approved.

## Deliverables and holds
Emit a motion-purpose matrix, runtime ownership and dependency map, reduced-motion equivalence protocol, source/viewport/version evidence plan, and immutable baseline/candidate receipt proposal. Status is always `DESIGN_PROPOSAL_HOLD_INDEPENDENT_QUALIFICATION` until actual representative browser measurements and user approval.
