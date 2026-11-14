# FAB.VISUAL Ω11E — Independent Camera/Frame Contract and Ray-Depth Model

Date: 2026-11-14. Research-only additive source; not a renderer or production release.

## Lineage and immutable source
Upstream: wheresryan22/anatomy at commit 1482e8469b0a9e0d8cc18ea2740a01423d29ae80; MIT Copyright (c) 2026 Ryan; 173 original tracked Git blobs preserved. Ω11E stacks on Ω11D draft PR #29 at b38b6963ba6c03f3db11a53945846d794decbb1b. No host, main, upstream or release changes.

Ω11D source-defined stages .rp-stage and .ts-stage PASS in two independently executed CI runs, while cross-process and cross-run screenshot reproducibility remained FAIL. Ω10B original generated HTML byte parity FAIL for three pages. These are not reclassified by an independent mathematical simulation.

## Additive independent substrates
1. schema/scene-frame-witness-omega11e-v0.1.schema.json: source-bound witness declaration with twelve evidence fields. Grades SOURCE_STATIC, RUNTIME_READBACK, DERIVED_WITH_ASSUMPTIONS and NOT_AVAILABLE express what is actually known, not the proof of a renderer event.

2. scripts/omega11e-frame-depth.py: standalone 4×4 matrix inversion with residual check; explicit OpenGL near/far NDC convention and metric coordinate units; finite near/far ray unprojection from a synthetically supplied view-projection pair; ray/triangle intersection producing ordered hit distances, triangle and part IDs, barycentric coordinates and face winding. Equal-depth and near-boundary cases become INCONCLUSIVE; malformed and nonfinite geometries, duplicate identities, singular matrices and invalid units are rejected. No actual Anatomy mesh or renderer is inspected here.

3. tests/test_omega11e_frame_depth.py: 20 adversarial tests of 3D synthetic ray geometry, matrix and viewport validity, boundary ambiguity, rejection of forged evidence and release-status preservation.

4. .github/workflows/fab-visual-omega11e.yml: exact-source GitHub Actions independent synthetic regression, original 173-blob lock, JSON Schema meta-validation, adversarial tests, hashed receipt archive. No browser or application host installation.

## Formal boundary
Let O be the camera ray derived from a supplied view-projection matrix, T the finite set of independently supplied model triangles, and I(O,T) the sorted visible ray hits with depth parameter t in model metres. The standalone algorithm establishes a deterministic ordering only within this synthetic model and within its numeric tolerance. It does not establish whether Anatomy used those matrices or triangles in the captured browser image, nor depth ordering under real SVG, alpha blending, occlusion, GPU rendering or motion.

The declarative SceneFrameWitness includes original source SHA, model SHA, scene ID, frame event ID, camera pose, projection, time/state, visible part IDs, viewport, renderer version and declared provenance. Even a user-supplied object with grade RUNTIME_READBACK and mutually consistent frame ID is NOT independently attested. frame_contract therefore never returns FRAME_VERIFIED: frame admission remains NOT_ADMITTED until an independent source-backed hook verifies the actual renderer state tied to capture.

## Adversarial controls
Test camera matrix non-invertibility; invalid near/far; incorrectly scaled coordinate system; degenerate triangle; parallel rays; grazing edges; two-part equal depth; ambiguous uncertainty band; reversed winding; duplicate IDs; malformed hash; source identity mismatch; forged and mislinked frame token; nonfinite data. Finite agreement is a synthetic software test, not production, physical, scientific or universally quantified visual validation.

## Admission ledger
SOURCE_LOCK: historical PASS, independently recheck in Ω11E workflow.
SYNTHETIC_CAMERA_RAY_AND_TRIANGLE_ORDER: PENDING independent exact-head CI.
DECLARATIVE_FRAME_SCHEMA: PENDING JSON Schema validation.
RUNTIME_RENDERER_FRAME_ID_ATTESTATION: NOT_ADMITTED.
REAL_ANATOMY_GEOMETRY_AND_OCCLUSION: NOT_RUN.
HISTORICAL_BYTE_PARITY: FAIL.
HISTORICAL_PIXEL_CROSS_RUN_STABILITY: FAIL.
HOST_INSTALLATION, WCAG, PHYSICAL_SWEPT_MESH, SCIENTIFIC: NOT_RUN.
RELEASE: HOLD.

## Next Ω11F
Research a source-hashed, read-only runtime adapter exposing actual frame event ID and rendered pose/projection tied to the verified full-size stage and a source-identified geometry mesh. The adapter must be independently validated and live only in a separately labeled disposable source-derived harness, never in the pinned original. Run independent ray/triangle ray-depth comparison against that actual scene only after model identity, world units and capture-frame consistency are established. Repeat cross-process image and macOS/Linux V8 build experiments; never automatically clear previous FAIL or authorize deployments.

No PR merge, upstream mutation, privileges, host changes, scientific or production release.
