# Anatomy ecosystem and candidate absorption — 2026-11-13

Source method: GitHub public API exact Git tree comparisons against `wheresryan22/anatomy@1482e84...`, read actual new code and repository metadata. File counts and changed paths compare snapshots, not necessarily all authored enhancements. New features are candidate designs, never admitted by popularity alone.

## Verified differentiated forks

| Repository | Status vs pinned original | Concrete innovation | Decision |
|---|---|---|---|
| [Reasonofmoon/anatomy-revised](https://github.com/Reasonofmoon/anatomy-revised) | 203 blobs; all 173 original paths still present; 30 new files, some upstream source files modified | `kit/fold.mjs`, callout avoidance and leader routing, text legibility and profile cleanups; unit tests | P0 candidate. Import **isolated callout algorithm + tests** only after license, source diff, trust boundaries, regression. Foldable mechanisms as optional P1. |
| [ochlodeep/anatomy-schematic](https://github.com/ochlodeep/anatomy-schematic) | 116 blobs; 18 new files, 75 original paths absent, many changed | `kit/schema.mjs`: datum, cellGrid, columns, plateStack, graph nodes/edges, tracks, height field; `references/schema.md` | P0 idea source for a *semantic* schema compiler. Never merge fork wholesale or use its unverified painter ordering as proof. |
| [jrramon/anatomy-lego](https://github.com/jrramon/anatomy-lego) | 65 blobs; ~30 new paths, 138 original paths missing | `kit/lego-audit.mjs` sequential support/attachment, grid constraints; `kit/lesson.mjs` step-by-step narrative/assembly | P1 discrete constructive proof checks and educational assembly model; LEGOs/brands require separate presentation permissions. Do not merge all. |
| [Charlyhno-eng/anatomy-codex](https://github.com/Charlyhno-eng/anatomy-codex) | 117 blobs; TypeScript conversion and Codex toolchain, 110 original paths absent | AGENTS.md, `package.json`: TS checking, preview server, browser, GIF export, Codex `$anatomy` skill install | P1 portability/TSC/quality ideas; consider independently reviewed adapters. The converted source is NOT byte-compatible upstream. |
| [yangshun2005/anatomy-cn](https://github.com/yangshun2005/anatomy-cn) | 148 blobs; README_en added, 26 original paths absent | Chinese-facing documentation, audience-specific instructions | P2 localization reference, no engine import. |
| [RianKoja/anatomy-skill](https://github.com/RianKoja/anatomy-skill) | exactly 173 blobs, identical Git tree SHA to pinned original | No independently identified source differences | CLASSIFY MIRROR. No evolution delta. |
| [47thtechcorner/RayCodes_AnatomySkill](https://github.com/47thtechcorner/RayCodes_AnatomySkill) | 7 blobs, mostly tutorials and five example standalone HTML outputs | educational prompts for mechanisms and example use cases | CASES ONLY; not an engine fork. |

## Cross-cutting principles

1. Preserve the entire original Anatomy skill untouched, including its examples, renderers, 3D/WebGL, scripts and PDFs.
2. Do not install or import a fork into the canonical submodule. Create an **evolution candidate** record with source URL, full Git SHA, SPDX/license, exact paths, semantic contribution, independent tests, attack surface, and decision.
3. On candidate admission, extract a small independent adapter or contribute the patch upstream. Enforce original Anatomy regression + model/visual consistency + host authority gates.
4. Respect license complexity. MIT adapters are simplest; LGPL/AGPL software requires deployment and distribution analysis. Never silently change upstream copyright.
5. Unknown functions and example-scoped shaders receive `RESEARCH` or `NOT_RUN`, never an unearned PASS.

## Neighbouring open-source lanes (NOT acquired)

- [jscad/OpenJSCAD.org](https://github.com/jscad/OpenJSCAD.org): parametric 2D/3D CSG and export, MIT; optional geometrical exactness gateway.
- [sgenoud/replicad](https://github.com/sgenoud/replicad): OCCT browser parametric solid authoring; license check before code intake.
- [donalffons/opencascade.js](https://github.com/donalffons/opencascade.js): WebAssembly OpenCascade, LGPL-2.1; optional exact CAD backend with licensing rules.
- [BOMWiki/partmode](https://github.com/BOMWiki/partmode): AGPL-3.0 typed human/agent CAD document kernel and exact B-rep; architecture reference only until AGPL review.
- [elchininet/isometric](https://github.com/elchininet/isometric): TypeScript SVG isometric primitives; geometry API comparison, no need to replace original.
- [jdan/isomer](https://github.com/jdan/isomer): Canvas isometric drawing; low-priority renderer portability reference.
- [mermaid-js/mermaid](https://github.com/mermaid-js/mermaid): text diagram DSL; alternative explanatory representation but not mechanical Anatomy replacement.
- [eclipse-sprotty/sprotty](https://github.com/eclipse-sprotty/sprotty): model-driven editor/reference; graph layout and model coherence candidate.
- [Kitware/vtk-js](https://github.com/Kitware/vtk-js): scientific volume/mesh views; separate scientific data integration candidate.
- [ManimCommunity/manim](https://github.com/ManimCommunity/manim): explanatory math animations; specialized renderer, not source replacement.
- [wonjyou/exploded-lens](https://github.com/wonjyou/exploded-lens): scroll-based 3D assembly part sequencing; UX reference.

## Order of absorption

P0 immutable full-source baseline and upstream native CI (this iteration) → P1 verified callout/annotation and diagram schema patterns as isolated FAB.VISUAL adapter prototypes → P2 narrative assembly and Codex toolchain portability → P3 optional CAD/VTK/Manim backends after license and claim contracts. No wholesale fork merge. 
