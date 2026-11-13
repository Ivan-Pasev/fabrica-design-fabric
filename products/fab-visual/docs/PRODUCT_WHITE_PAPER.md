# FAB.VISUAL — Model-Governed, Evidence-Carrying Visual Archetonics

**Technical Product White Paper | v0.2.0-alpha.0 | 2026-11-13**

## Abstract

Complex software, cybernetic controllers, engineered energy systems and mathematical research need explanations that remain faithful to their source models. A graphic can be internally consistent while contradicting its authoritative calculations or claiming more than the evidence supports. FAB.VISUAL proposes a typed semantic scene, source-linked observables, specialized visualization engines and independently recorded evidence gates. The first reference runtime implements model validation, deterministic SVG/HTML output, a synthetic policy-machine demonstration and a portable non-invasive CodexStation extension candidate. The external Anatomy project motivates mechanical explanatory geometry and audits but is not bundled or fully integrated into this alpha.

## Problem statement

Modern visualizations mix at least four kinds of authority: the physical/mathematical model, the depiction, a narrative, and a publication claim. If these disagree, users may accept a persuasive but false illustration. Conversely, a complex auditing tool may report success on only a finite sample. The system must preserve both usefulness and proof boundaries.

## Prior art and source mapping

Anatomy, MIT (Ryan, 2026), at commit 1482e8469b0a9e0d8cc18ea2740a01423d29ae80, provides a craft workflow, procedural isometric SVG, round/tube components, WebGL effects, beta articulated motion, geometry checks and printable technical sheets. Its public source and open PRs reveal finite sampled overlap failure for subpixel wires, 3D ordering and runtime hardening needs, reduced-motion transitions and output registry collisions. These are reasons for bounded verification, not arguments against adoption. CAD, scientific data visualization and mathematical animation should remain separate adapters with their own authoritative semantics.

## Proposed system

(1) Source authority and provenance; (2) typed semantic model/observables and units; (3) SceneIR with stable components, relations and claims; (4) independent or specialized rendering; (5) verification and human review; (6) release and distribution through explicit authorization.

Core types: `PHYSICAL`, `ANALOGICAL`, `FORMAL`. A model object includes identity, revision and authority. A scene includes component dimensions, parent links, typed relation edges and observables. Release evidence includes source, model, state, geometric and publication-specific checks. The current reference output is independent SVG, not upstream 3D geometry.

## Mathematical semantics

Let M be a model, s an admissible state, O(M,s) its declared observable vector, R(G(s)) its visualization, D the readout extractor, and epsilon_o a per-observable bound. The conditional contract is |D_o(R(G(s))) − O_o(M,s)| <= epsilon_o for each tested numeric observable; booleans and strings require equality. Evidence must record the actual tested set; finite sampling does not prove all continuous states. Parent/child refinement is a typed relation rather than viewport zoom, with containment DAG independent from legitimate cyclic signal feedback.

## Research-to-product pipeline

Acquire → license review → exact source manifest → source audit → typed model/claims → geometry/compiler → model consistency tests → independent renderer checks → restricted browser inspection → evidence ledger → human release authority → versioned artifact. No phase may infer scientific or host authorization from graphic quality.

## Implemented alpha

An independent Node ESM CLI provides `validate`, `render`, `demo`, `anatomy-plan`, `inspect-upstream`, `gate`. SceneIR consistency tests, evidence receipts, synthetic policy timeline and CodexStation additive installer are locally executable. No external services are required for the tests. Source lock verifies a cloned upstream git commit if it is present; absent upstream fails closed. We do not claim integrated upstream geometry or actual CodexStation deployment.

## Safety and limitations

Untrusted source can contain instructions, malicious code or compromised browser assets. Browser testing of upstream HTML/JS must occur in isolated, network-restricted workers. Geometry audits must preserve approximation and resolution limitations. Engineering figures cannot be certified merely by deterministic output; mathematical visualization cannot certify a theorem. Privacy, input trust, copyright and publication rights require separate review.

## Intended product cases

Computational: a policy authorization mechanism with its exact transition and audit record. Physical: a storage system where energy conservation, units and measured/assumed values are explicit. Formal: a theorem dependency and counterexample explorer where visual analogies are not proofs. Academic publication: consistent identifiers across article figures, HTML supplements and machine-readable evidence.

## Roadmap

Ω4A: exact source inventory, alpha reference runtime, evidence ledger, CodexStation install candidate. Ω4B: checkout and reproducible Anatomy integration with real kit call and geometry tests. Ω4C: independent geometry oracle, narrow-pipe/curve regressions, browser isolation and accessibility. Ω4D: recursive semantic descent, CAD/VTK/Manim adapters and publication outputs. Ω5: audited v0.1 external release once security, claims and rights gates pass. Each release must state both verified functions and outstanding debt.

## Conclusion

A visual artifact is a research object with a model and evidence boundaries—not a decorative picture or an automatic proof. FAB.VISUAL aims to make that distinction executable while exploiting high-quality explanatory substrates without surrendering constitutional authority.
