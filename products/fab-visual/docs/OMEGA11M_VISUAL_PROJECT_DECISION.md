# FAB.VISUAL Ω11M — Source Forks, Revision Diff, Accessible Connectors, Portable Visual Projects

**Product candidate:** v0.7.0-alpha.0 · **Status:** bounded local functionality under test, RELEASE HOLD.

## Architectural scope and actual functionality

Implemented first-party `src/visual/project.mjs` pure primitives: `forkVisualScene` for visual-only derived SceneIR and distinct visual model revision; `visualDiff` for source-vs-derived changes to geometry, labels and source-typed illustrative edges; `zipStore` for deterministic STORE/CRC32 ZIP; and `projectFiles` for a portable archive of original scene, fork, diff, bounded revision history, manifest and readme. The portable archive is an actual standards-readable ZIP, not a JSON file renamed `.zip`. `bin/fab-visual.mjs project` produces the ZIP plus SHA-256 receipt.

The already-operational offline Studio now embeds these primitives without network dependencies. User actions: choose source/derived revision in an actual 2D side-by-side diff, inspect exact moved/resized IDs and added/removed links, fork current visual scene from a validated lowercase slug, download original-source-anchored ZIP with explicit local edit history, and select typed canvas connectors from actual SVG components/edges with pointer and keyboard (Enter/Space). Undo/redo survives link changes. Existing source-pinned Anatomy view remains unavailable after edits until a verified recompile.

## Constitutional invariants

**I-1 Immutable source:** Each fork records original source SceneIR ID, model ID, model revision, canonical SHA-256 content correspondence and an explanatory visualRevision. The exact original is packaged unchanged and is not rewritten in the repository or browser.

**I-2 Authority boundary:** Original `model.id`, `model.authority`, claim/status, source observables, audit and domain template metadata are preserved; only visual coordinates/labels and illustrative typed edges may change. The fork's `model.revision` is explicitly namespaced `+visual-fork.<slug>` and never presented as a verified scientific, physical or authorized model revision.

**I-3 Port and structure:** Source component IDs, source-defined ports/status/hierarchy, finite bounded geometry and allowed flow categories are validated. Invalid/dangling endpoints, malformed source digest, traversal slugs, duplicate ZIP paths and forged release/publisher fields are rejected.

**I-4 Evidence limits:** ZIP CRC32 protects transport only; ZIP is not encrypted or digitally signed. Source SHA-256 indicates content correspondence to the original provided SceneIR, not authentic publisher identity. `publisherSignature: NOT_PRESENT`, `physicalValidation: NOT_RUN`, `hostAuthorization: NOT_RUN`, `real GPU present: NOT_ADMITTED`, `release: HOLD` are nonpromotable without independent evidence.

**I-5 No external side effects:** Local project actions use Blob downloads; no private data ingestion, network, managed SQL DB, Google Drive autosync, live CodexStation agent execution, main merge or Cloudflare/host deployment.

## Executable user commands

```bash
cd products/fab-visual
node --test tests/*.test.mjs
node bin/fab-visual.mjs gallery dist/gallery
node bin/fab-visual.mjs project templates/energy-microgrid.scene.json templates/energy-microgrid.scene.json study01 dist/study01.zip
```

Local project ZIP entries: `manifest.json`, `source/original.scene.json`, `derived/fork.scene.json`, `evidence/visual-diff.json`, `evidence/edit-history.json`, `readme.txt`. The ZIP is portable for offline inspection; direct trusted ZIP import into Studio is NOT_IMPLEMENTED. The original SceneIR input must be explicitly reopened for subsequent scene review.

## Test campaign and adversarial checks

At the first complete review-head CI [#43603746633](https://github.com/Ivan-Pasev/fabrica-design-fabric/actions/runs/43603746633), **176/176 Node tests passed** (20 new Ω11M tests), along with original 173-object pinned MIT Anatomy source lock and prior Studio/Gallery Chromium browser regressions. The new Chromium three-domain product test exercised source-vs-revision visual diff, keyboard/mouse source typed connector selections, reversible edge removal, user-visible derived SceneIR fork download, independently `zipfile`-readable project ZIP and manifest/claim invariants, and rejected unsafe fork identifiers.

Explicit negatives include status/claim/authority drift, changed observables or template/audit, invalid fork provenance, malformed SHA/slug, duplicate/missing model IDs, unsafe ZIP names, invalid port and nonfinite coordinates. The full exact HEAD and independent second CI run will be linked on draft PR after final documentation commit. Do not equate these bounded browser outcomes with verified GPU/compositor presentation or any scientific admission.

## Source and external-library portfolio

Original MIT `wheresryan22/anatomy` pinned to `1482e8469b0a9e0d8cc18ea2740a01423d29ae80`, all 173 original Git source blobs unchanged. New Ω11M components are first-party and dependency-free. Existing XYFlow/Cytoscape format projections are NOT verified against pinned external editor runtime installations. Excalidraw and other optional runtimes remain candidate/HOLD until actual license/ABI/source pin review.

## NEXT_0019 Ω11N provisional user-value focus

Build a real visual project import/open/replay workflow for the new portable ZIP, including strict evidence gate and original-source digest validation; add local project gallery with revision cards; test actual XYFlow/Cytoscape runtime schema compatibility separately. Do not push real deployment, DB service, science claims or model authority ahead of product user experience.

**Disposition:** first-party offline visual fork, diff, connector and portable project functionality demonstrated under bounded test conditions; production/scientific/release gates remain HOLD.