# FAB.VISUAL Ω11A — Independent 3D clearance research gate

Status: candidate only. Parent Ω10B PR #25 at 745d800476fb4642749799af87918e37d5508fba. Strict generated Anatomy HTML byte parity remains FAIL (three files); bounded numerical diagnosis is PASS; release HOLD.

## Mathematical contract
For a finite straight segment S=[p0,p1], static axis-aligned box B, and nonnegative radius r, compute d = min_{x in S,y in B} ||x-y||. Break the parameter interval at all AABB plane crossings; on each subinterval the squared distance to the AABB is a quadratic and admits a closed-form minimum. Define signed margin m=d-r. With explicitly declared spatial uncertainty u and numerical epsilon e:
- m > u+e => CLEAR within this idealized model
- m < -u-e => INTERSECTS within this idealized model
- otherwise => INCONCLUSIVE

All coordinates, radii and tolerances share one explicitly declared unit (m or mm). Port tests only compare endpoint-to-center distance, not connector orientation, surface penetration or continuity. A sampled-motion CLEAR is conditional on a correctly established upper bound for each endpoint speed across all intermediate times; the software cannot verify this assumption from samples.

## Implemented independent tests
12 adversarial synthetic tests of crossing, endpoint/degenerate cases, interior stationary closest distance, tangency, epsilon and uncertainty bands, port boundary, motion speed-bound dependency, sampled intersection, invalid input and ordering. Local Python stdlib execution 12/12 PASS. Independent GitHub Actions workflow is supplied; its status must be read from the exact run before admission.

## Claim boundaries
No import or modification of the original Anatomy 173-blob MIT-licensed source. No bridge to actual SceneIR runtime, actual 3D mesh/cable motion, screen-space occlusion, renderer verification, validated physical units from a device, accessibility certification, live CodexStation installation, source parity repair, publication or host authority. No automatic merge.

## Next checks
1. Verify CI on exact source head and freeze Actions receipts.
2. Source-preserving fixed-browser screenshot/camera-state diffs on original versus rebuilt three pages, including discontinuous visibility and depth event tests.
3. Independent actual mesh/convex-body and bent/tube geometry validation; AABB is conservative proxy only.
4. Verify speed-bound provenance and interval coverage, or retain INCONCLUSIVE.
5. Compare pinned Node/V8/architecture and repeated macOS/Linux output with original committed bytes intact.
6. WCAG with assistive technology, 400% zoom, Firefox/WebKit, owner-host ABI review; release remains HOLD.

## Invariant ledger
STATIC_AABB_ORACLE = CANDIDATE
LOCAL_SYNTHETIC_TESTS = PASS (12/12)
INDEPENDENT_CI = PENDING_VERIFICATION
ORIGINAL_REBUILT_BROWSER_PARITY = NOT_RUN
TRUE_WORLD_SPACE_MESH_CLEARANCE = NOT_RUN
MOTION_SPEED_PROVENANCE = NOT_RUN
STRICT_GENERATED_BYTE_PARITY = FAIL
LIVE_HOST_AUTHORIZATION = NOT_RUN
RELEASE = HOLD
