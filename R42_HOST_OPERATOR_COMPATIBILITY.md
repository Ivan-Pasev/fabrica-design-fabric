# R42 — Host operator compatibility: Design Fabric is subordinate

**Draft FDF review profile, not a local IDE session.** This profile makes FDF's generic design process compatible with hosts whose own AGENTS.md or runtime constitution distinguishes read-only planning from editing, packaging and deploying. It contains no copied private project control documents or source code.

## Safe host integration

The existing IDE/project master remains authoritative. In a host with a governed operator grammar:

| Host operation | FDF action | Allowed state |
| --- | --- | --- |
| `STATUS()` | Read local HEAD, dirty state, version, active priority, pending proposal | read-only |
| `NEXT(UX)` or `NEXT(UI)` | Survey ProjectDNA, evaluate 1 high-value defect, propose file-scoped reversible change | read-only, pending proposal |
| `REVIEW()` | adversarial critique of current diff | read-only |
| `CHECK(domain)` | host's existing targeted validators | tests-only as host permits |
| `CONTINUE()` | only a host-valid accepted pending proposal after actual local ref/policy freshness check | host-only authorized mutation; FDF itself grants none |
| `PUBLISH()` | packaging through host's canonical pipeline | separate permission; not deployment |
| `DEPLOY()` | remote change | separate human action; never assumed |

The FDF external injection prompt **must not** describe itself as blanket permission to edit. The optional `tools/fdf_host_operator_gate.py` only classifies declared operator intent; even a `HOST_CONTINUE_PREFLIGHT_ONLY` result is not an authorization. Actual host law, dirty tree, user grant, scoped paths and executable checks must be read and enforced by the existing IDE master. Existing project instructions are reference material to the FDF adapter, not documents to be copied or modified.

## Scientific VitePress research host profile (ivanpasev.com example)

This example reflects a host design program with VitePress corpus, strong authorial provenance, existing agentic roles and a no-silent-deployment policy. It is an operator *pattern*, not a claim to have inspected its local Windows source:

- Treat the host's science/publication integrity work as higher priority than gratuitous UI polish. An active publication-integrity gate remains open until the host's local master verifies it.
- Seek a **concrete reader-architecture defect** (for example, a very long scientific route without a legible evidence/limitation pathway). Do not reopen already-verified shared shell, navigation, responsive geometry, or focus primitives without reproduced defects.
- First invocation: `STATUS()` → `NEXT(UX@reader-architecture)` → one pending proposal and evidence plan. **No edit**.
- Second invocation, *only if the host master and owner admit the fresh pending proposal*: `CONTINUE()` on one scoped component/route, then actual host-specific `CHECK(UI+UX)` and `REVIEW()`. Do not invent test results or write a competing local agent constitution.
- Site design should remain institutional, restrained, accessible and high-information; prioritize clear proof/evidence/limit linkage, typography, in-page reading sequence, reader journeys and stable canonical URLs rather than generic SaaS patterns, ornamental gradients or global redesign.
- Keep the distinct meanings of theorem, experimental result, comparator, negative finding, simulation and manuscript status; never turn a design presentation change into scientific-status promotion.
- Host manual-only deployment: no auto push, version bump, package, publication or live domain change.

## Two paste-ready invocation phases

### Phase A — first host call (read-only)

> FDF::HOST_INTEGRATE / STATUS() / NEXT(UX@reader-architecture). Rehydrate the current IDE project from its own local AGENTS.md, repository, canonical host control and active handoff. Use the exact pinned FDF review SHA only as a subordinate advisory DesignSkill reference. Respect operator non-equivalence: NEXT means propose and stop; this instruction grants NO mutation, install, commit, publish or deploy authority. Audit one verified scientific reader-flow defect and return one reversible, file-specific pending proposal with actual local HEAD, dirty state, validation cases, rollback and owner gate. If the host's active science/release work makes design work unsafe, return HOLD or NO MATERIAL INTERVENTION JUSTIFIED. Preserve research evidence boundaries.

### Phase B — separate invocation only after approval

> CONTINUE() the *explicitly accepted current host pending proposal*, if and only if the local agent independently confirms its own authority, unchanged source HEAD/policy/dirty state, allowed paths and rollback. Scope the implementation to the accepted UI slice. Run real host validators, a genuine desktop/mobile/keyboard observation, preserve private evidence outside public distribution and report precise PASS/FAIL/HOLD. If no pending proposal or permission, return HOLD. Do not publish, deploy, change scientific claims or modify unrelated work.

## Evidence and limitations

FDF R41's two-phase before/after kit can record receipts only when a real external owner-invoked local IDE trial occurs; its hashes/PNG structure/log files do not attest to session genuineness or semantic correctness. This R42 host operator contract can be tested as software, but source-only CI never proves a real integration. Human approval, effective main protection, real test replay and independent review remain open.
