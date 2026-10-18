# FDF/EK-001 — Emil Kowalski skills adoption candidate

## Discovery / license
- Upstream source: https://github.com/emilkowalski/skills at exact commit `2d228630ba1446365f614a108cb8252f1feda202`.
- Verified snapshot: **15** upstream `SKILL.md` assets, **8** skill-specific supporting reference docs; MIT license, copyright (c) 2026 Emil Kowalski. Each SKILL.md has a pinned source Git blob in `registry/upstream-emil-kowalski.v1.json`.
- Upstream install instruction in README: `npx skills@latest add emilkowalski/skills`. **Do not execute this** during source discovery, IDE admission or FDF kernel routing: it is unpinned and may mutate the caller/agent environment.

## Deep architectural classification
The upstream repository is principally Markdown instructions, reference guidance and recipes, not a privileged executable design runtime. Motion design, performance diagnosis, Expo/React Native, Apple-inspired motion, Swift, library choice, Sonner and adverse-state UI inspection are distinct capabilities. The original skill text is lower-trust project input when read by an agent.

| FDF capability | External references | Admission |
| --- | --- | --- |
| Motion direction / build planning | animate, animation-performance, animation-vocabulary | propose only; tests and user approval before edits |
| Expo / native motion | animate-expo | Expo context required; dependency installs separately approved |
| Critique, audit and discovery | emil-design-eng, improve-animations, find-animation-opportunities | evidence-oriented read-only assessment |
| Stress / mobile parity | break-ui, mobile-native | worst-case data only in isolated tests; no production toggles |
| Explicit-only user tools | prototype, pick-ui-library, review-animations | preserve `disable-model-invocation: true` |
| Platform/specific styling | write-swift, ask-sonner, apple-design | scoped Swift / Sonner / owner-invoked Apple style |

## Project authority / tuned mutation
The original upstream `animate`, `animate-expo`, `prototype`, `break-ui` and `write-swift` documentation can instruct an agent to implement changes. **FDF never converts this upstream permission into caller authorization.** Actual design decisions require caller project identity, honest product facts, verified file references, explicit owner permission, reduced-motion and accessible functionality, performance measurement, and rollback. `review-animations`, `prototype`, `pick-ui-library` are deliberately explicit-only; `apple-design` is additionally brand opt-in.

## Architecture and portability
The original source stays upstream and pinned; only the registry, FDF bridge `SKILL.md`, a deterministic read-only Python resolver, tests and attribution are staged. No npm install, git submodule, hidden vendor mirror, private jury maps, modifications to existing kernel policy or automatic execution. Optional R35/R36 evidence runners remain separate. Do not promote source-only tests to proof of real IDE use, aesthetics, WCAG or GPU.

## Latest host-operator compatibility
The R42 host-aware FDF review stack is the integration base. Its `R42_HOST_OPERATOR_COMPATIBILITY.md` takes precedence over upstream motion-build instructions; only host-authorized STATUS/NEXT read-only actions are eligible for automatic planning. CONTINUE/PUBLISH/DEPLOY are not granted by this bridge or a source reference. The host's current project/research integrity gates always outrank general aesthetics.

## Trust, provenance and release
This is reference-mode adoption (not a source fork). Upstream Git commit and 15 individual SKILL.md Git blobs are locked in the JSON registry; the MIT notice is linked and correctly attributed. FDF policy `RELEASE_POLICY.md` forbids third-party skill bundles: no exceptions silently introduced. Upstream updates require diff, license/security recheck, per-skill admission review and new pinned manifest version. **Draft PR only**; human review/protected-main/real local IDE qualification/public v1 remain HOLD.

## EK-002 — host-bound evolution (additive)

The first bridge's `--project-known` flag is only a declaration; it cannot establish that the caller project was inspected. The additional `tools/fdf_kowalski_host_route.py` composes previously reviewed R40 ProjectDNA and R42 host-operator preflights with the EK pinned-reference router, and introduces a separate schema `fdf.kbi.ek-host-route/0.1`. For a selected skill, output includes current UI observation digest, receipt fingerprint, narrow coverage admission, host-policy file count and **explicit false** flags for IDE execution, owner authorization, upstream execution and authenticated operator policy.

A known host precheck is necessary, never sufficient: all selected references remain propose-only. No policy semantic content is copied into receipts. A stale/forged previous receipt is rejected by recomputing the host binding. A continued or publish/deploy operator bypasses scanner execution and returns HOLD; the host master alone determines those actual authorizations.

Limits: heuristic source scope only; no validation of the declared framework or FDF commit; no complete caller source-map; no actual browser, visual, keyboard or assistive-technology run; no evidence that this command ran inside the owner's IDE. No third-party source vendoring; all R43+ host priorities stay intact.
