# FAB.VISUAL Ω11L — Three Domain Starter Packs and Editable Offline Gallery

**Scope:** first-party SYNTHETIC topology product functionality; not real device design, scientific admission, production deployment or agent authorization.

## 1. Operational architecture and source boundaries

Source-verified upstream Anatomy: wheresryan22/anatomy Git commit 1482e8469b0a9e0d8cc18ea2740a01423d29ae80 (MIT; 173 original tracked Git objects independently checked and immutable). Feature work is additive to unmerged FAB.VISUAL Ω11K PR #36; no main merge or host permissions.

A new domain template catalog is assembled from three original SceneIR v0.2 JSON files and the source-aware, strict validator in src/visual/gallery.mjs. Gallery CLI:

    cd products/fab-visual
    node bin/fab-visual.mjs gallery dist/gallery

Generates exactly **11 portable files**:
- one searchable, filterable, no-network Gallery index HTML;
- three standalone offline editable Studio HTML applications under studios/;
- three original SceneIR JSON templates under scenes/;
- three independent SVG previews under previews/;
- gallery.manifest.json with per-artifact SHA-256 and source digests.

The gallery folder must be kept together for local navigation. Each individual Studio HTML is standalone. Entire build has no runtime external JS/CSS imports, no private knowledge ingestion and no managed SQL/cloud dependencies.

## 2. First-party capability packs

**Citizen Solar microgrid (6 components / 7 typed links):** synthetic PV array, battery storage, DC bus, inverter, load and dispatch controller; typed energy, information and control edges. Export power is NOT_CALCULATED, battery SOC NOT_MEASURED, and no energy yield, LCOE, commercial feasibility, regulatory grid interconnection or equipment safety is asserted.

**GILC experimental DAQ (7 / 8):** sample inlet, isolation chamber, pressure transducer, optical detector, DAQ, pump and safety interlock; typed material/signal/control edges. Pressure NOT_MEASURED, exposure NOT_ASSESSED, calibration NOT_RUN. It is not a built device, validated BAS experiment or safety engineering certificate.

**CodexStation evidence/approval (7 / 7):** human request, planner, research collection, independent verifier, policy gate, human approval and BLOCKED execution. Synthetic agents and pipeline, real operator approval=false, external execution=false. It does not connect live agents, establish consent or grant operational authorization.

Every SceneIR source declares template origin FIRST_PARTY_SYNTHETIC, model authority explicitly synthetic, numerical observables with explicit unit and source, evidence status NOT_RUN, and claim EXPLANATORY. Domain validators reject forged real measurements, scientific admission, live-host authority, duplicated/dangling topology, unsupported port units or claim promotion.

## 3. Actual Studio evolution beyond gallery

New reversible connection removal complements the prior creation of illustrative typed links and numeric component layout edits. Existing visual snapshots can be undone/redone. A user-initiated local edit-history download includes original scene digest and bounded snapshots with publisher signature NOT_PRESENT and release HOLD. There is no hidden auto-save, cloud mutation or status-authority transfer.

After any local scene edit, stale source-pinned Anatomy 3D/isometric and comparison views are disabled until a new SceneIR is recompiled and checked. Editing and source graph exports cannot turn illustrative diagrams into physical clearance, verified computation or authorization.

The original source file is never overwritten by the gallery. Normal edits download separate derived files, and only tested first-party, versioned XYFlow/Cytoscape transport envelopes with a matching original source scene are imported.

## 4. Executable acceptance

Initial repaired full CI #43595104888 passed inherited Node tests, exact 173-blob source lock, three SceneIR Gallery package creation, original 2D/isometric Studio browser smoke, and all three Gallery page filter/navigation/source-bound editor interaction tests under isolated Chromium.

Additional editor functions and new negative tests progressed through later CI runs. The final documentation head must receive a separate exact-head successful CI and an independently repeated execution before a final PASS attestation. Every archived CI receipt should preserve the exact HEAD, Node test total, Chromium version, gallery manifest, three source scene checks, Git original status, checksum manifest and each downloaded edited scene/history.

A successful rendered screenshot or a browser DOM event is **not** an independent GPU/compositor presented-frame attestation. Source SHA equality is content correspondence, not an authenticated source publisher signature.

## 5. Adversarial and license obligations

- Reject nonfinite or oversized layouts, unsupported node identities and typed link ports, cyclic containment and dangling flows.
- Reject live sensor readings, secret/medical data, fabricated metrology, source authority or approval escalation and claimed scientific certification.
- Escape model labels, reject external active content and block browser network requests under strict page CSP.
- Keep immutable original MIT Anatomy source and attribution; no other third-party editor runtime introduced or source copied.
- Preserve inherited historic 7 FAIL / 1 HOLD and all weaker evidence boundaries, with no automatic register promotion.
- User-visible Gallery is a research alpha artifact; production release HOLD.

## 6. NEXT — Ω11M capability priorities

Enhance onboarding and realistic editing **without a DB-centred milestone**: add source-typed visual connectors with accessible hover/click behavior, local scene version comparison/diff, duplication/forking of synthetic domain templates, and a portable export bundle that aggregates a Gallery custom scene set. Validate package-install runtime compatibility, fixture source provenance and third-party editor bridges separately. Do not add fake grid metrics, lab results, or agent execution claims. Central SQLite should remain a subordinate evidence index.

**Disposition:** code-first product capability increment; real-world scientific, physical, permission and release gates remain HOLD or NOT_RUN.
