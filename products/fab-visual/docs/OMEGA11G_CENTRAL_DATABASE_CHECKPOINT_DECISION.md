# FAB.VISUAL Ω11G — Central SQLite Evidence Spine and Applied-State Checkpoint Decision

Date: 2026-11-14.
Claim boundary: research-only additive implementation; not a deployed data service or physical/renderer certification.

## 1. Immutable ancestry

Original upstream wheresryan22/anatomy is pinned to Git revision 1482e8469b0a9e0d8cc18ea2740a01423d29ae80, MIT Copyright (c) 2026 Ryan. All 173 original tracked Git objects are independently verified and original working tree remains unchanged.

The first-party research branch feature/fab-visual-omega11g-central-db-checkpoint stacks on Ω11F draft PR #31 at fb438aeedf64312374e675d466303efbd3dcfccc, which stacks on Ω11E PR #30. Main branch, CodexStation hosts, upstream code, permissions, and release state are not changed.

## 2. Central database identity and transaction model

Central directory: https://drive.google.com/drive/folders/1aaxBJfb1YnABgNuDhInMEueXisKlZO8v.

The database is a portable SQLite 3 research snapshot produced in source-locked independent CI. The core schema includes sources, gate_events, evidence, ci_runs, checkpoint_events, metadata, plus gate_current and gate_counts views. Foreign keys, CHECK constraints and append-only triggers protect provenance, statuses and checkpoint claims. SQL validation includes PRAGMA integrity_check, PRAGMA foreign_key_check and cryptographically hashed receipts.

Initial source import consists of 32 canonical gates, 35 evidence references and two previously verified Ω11F CI runs. The source of current gate status remains the existing native Google Sheet https://docs.google.com/spreadsheets/d/1Hn8MoTf-AFbcIZuQyskBneo4iPnA9y00HJWUrGJqn7M/edit: Gate Registry A7:H38; Evidence Sources A2:E36. This SQLite DB is a source-stamped, append-only projection, not yet the exclusive online authority and not automatically synchronized.

After exact-head Ω11G Chromium evaluation, eight derivative checkpoint entries are appended: four minimal-checkpoint controls with no detailed source state, four observing-checkpoint entries with SHA256-attested applied-state JSON snapshots. Four unmodified source-browser processes are independently checked and do NOT get fabricated checkpoint records. A new CI source is inserted, yielding three CI-run rows. Exact source html hashes, derivation variant hash, code HEAD, run ID, scene identity, stage identity, ordinal=3, and nonadmission boundaries are captured in separate machine receipts.

The file DB_SNAPSHOT_RECEIPT.json identifies the initial database SHA before checkpoint ingestion; CENTRAL_DB_FINAL_RECEIPT.json identifies the final post-ingestion database SHA. Only the latter validates the final SQLite bytes. No old receipts are overwritten.

The canonical archival package includes the final binary SQLite database, machine receipts, source lock, full browser matrix and screenshots, unit test logs and per-file SHA256SUMS. The schema and builder remain in first-party GitHub draft source. An always-on SQL service, automatic CI-to-Drive synchronization, scheduled sync, or live API is NOT DEPLOYED.

## 3. Ω11G controlled applied-state experiment

Two source-verified disposable derivatives are built per original page. MINIMAL_CHECKPOINT increments an in-page update ordinal and stops scheduling after actual source update 3; OBSERVING_CHECKPOINT uses the identical stop-on-three scheduler while capturing detailed closure-local state. The control is not an entirely zero-overhead observer; both variants intentionally intercept scheduling and are separately hashed test derivatives.

Raptor light hook executes after DOM placement and idle readout in the original animation tick. It records part spring positions and targets, assembly selection, explosive/burn state, and D.camera as static embedded GL data. Turning dial stress hook executes immediately after the actual controller.set({table: angle, lift:1, time}) call, not when an update is skipped by its throttle. Both scenes' actual stages .rp-stage and .ts-stage are selected.

The Chromium experiment uses two fresh browser processes for each scene and each source side: original, minimal checkpoint, observing checkpoint. This is 2 scenes × 3 sides × 2 fresh processes = 12. Four original pages must have no injected hooks. All eight derivative instances must stop at source application ordinal 3 and preserve the nonadmission guard. This is an application-update checkpoint, NOT independently attested renderer-present barrier, GPU depth buffer, camera pose or synthetic geometry-to-model match.

Source time advances under uncontrolled RAF. Therefore equal application ordinal is demonstrated, but equal elapsed time, equal physical state, causal absence of observer perturbation and screenshot bitwise repeatability are not established. No three-dimensional model mesh/part depth comparison or physical clearance is performed.

## 4. Independent executable evidence

First complete independent CI: https://github.com/Ivan-Pasev/fabrica-design-fabric/actions/runs/43573628843 at reviewed source HEAD 19700055a5a86cd3a08a759d956ec28a106cd816. Result SUCCESS; all 48 adversarial Python tests PASS, including 16 central DB tests, 18 source-derivative checkpoint tests and 14 SQLite ingestion tests; independently locks original 173 Git objects, validates all 12 Chromium process receipts and source-defined stage dimensions, ingests 8 unique checkpoint records into SQLite, preserves 32 source gate statuses, validates SQLite foreign keys and final SHA, and hashes all evidence files. The original remains untouched.

Independent artifact saved at https://drive.google.com/file/d/1ul7zcuKHzsGHjItxiqRsahEzsOJyTJ8k/view. SHA-256 of the downloaded ZIP: 65815fa296fe8beb1cfb864b9bf28dc41df62932ab4b802e6d4f3b2aa606ec80. SQLite final DB sha256: 7987a1559ea9c4ef4c3a19dbfaa30c03c4ec3f6f99342fd98f3e7915efe50beb (98,304 bytes). The final receipt explicitly states eight derivative checkpoint rows, four detailed application-state snapshots and four unmodified originals.

## 5. Adversarial status and release gates

Bounded software gates: original source lock PASS, central DB build and integrity PASS, 48 adversarial regression controls PASS, twelve-process fixed application ordinal PASS, source-grounded eight-row SQLite ingestion PASS.

Separately not admitted: runtime GPU-present barrier NOT_ADMITTED; source-verified dynamic camera pose/projection NOT_ADMITTED; real mesh/3D occlusion/physical clearance NOT_RUN; exact equality of source state across uncontrolled RAF processes INCONCLUSIVE; observer perturbation equivalence NOT_RUN; automatic central database service and bidirectional sync NOT_IMPLEMENTED.

Historical failures retained without reinterpretation: original three-page generated HTML strict byte parity FAIL, actual-scene cross-process/cross-CI image reproducibility FAIL, Ω11F uncontrolled sample-count repeatability FAIL. Production release HOLD; no merge or host deployment.

A successful source-locked derivative test does not validate commercial engineering, external scientific claims, renderer parity, or physical metrology.

## 6. Next bounded mutation

Ω11H should introduce an explicit source-compatible virtual RAF schedule with initial-state control for the minimal and observing derivatives, measure intervention overhead, and test state-signature agreement with a clock model verified to preserve the source's expected semantics. A real browser painted/composited frame attestation is a separate requirement. Actual geometry and depth ordering must remain NOT_RUN until source-identified mesh, transforms, camera and a frame token are independently bound.

Database evolution v0.2 requires a reviewed reconciliation protocol between later native Sheet revisions and append-only new gate-status events; never silently convert stale v0.1 seed records to current authority. Cloud-hosted SQL deployment is outside this PR and requires explicit authorization, authentication, backup and governance.
