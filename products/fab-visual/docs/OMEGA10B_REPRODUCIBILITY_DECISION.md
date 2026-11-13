# FAB.VISUAL Ω10B — Cross-platform serialized-output diagnosis

**Research candidate:** fail-closed diagnostic only; no production or scientific release authority.

## Reproducibility predicates

The original pinned Anatomy Git commit `1482e8469b0a9e0d8cc18ea2740a01423d29ae80` remains unmodified. Independent Ω10 Linux CI passed all 290 upstream Node tests and executed all sixteen build invocations. However, three generated HTML pages differed in bytes from committed upstream outputs; the strict byte-reproducibility criterion therefore failed. Green functional tests and byte-identical builds are distinct predicates.

## Exact differences isolated from immutable original vs independently generated local outputs

1. `examples/raptor-engine/raptor-engine.html`: only four numerical JSON values differ inside `const D`; all other JSON fields and surrounding HTML are identical. Changes are at `V[2]`, `camera.k`, `camera.cam[2]`, and `exit[1]`; maximum absolute difference `5.684341886080802e-14`.
2. `examples/raptor-engine/raptor-engine-light.html`: exactly the same four numerical differences, with identical surrounding HTML.
3. `examples/turning-dial/turning-stress-light.html`: only the base64-packed `const DATA.framed.hand` differs; all other JSON fields and surrounding HTML are identical. Of **5,443 ten-byte packed records**, five have changed 16-bit octahedral normal codes. All three 16-bit identifiers per changed record are identical. Four code pairs differ by one least-significant quantization step; the fifth uses two distinct octahedral encodings that reconstruct effectively the same direction at the fold seam. Maximum reconstructed unit-normal L2 delta: `3.487366062589921e-05`.

## Cause status and limitations

The differences are **consistent with** platform-/floating-point-sensitive calculation and quantized normal encoding. This identifies the affected fields; it does not establish the exact causal instruction, browser-image equivalence, geometric constraint equivalence, or scientific correctness. A quantized normal angle/length bound is not a proof of harmlessness to downstream discrete ordering, contact or occlusion logic.

## Implemented closed-world classifier

A source-locked Python diagnostic parses the three original HTML `const D`/`const DATA` objects without executing JavaScript or loading network assets, hashes original files against their exact source digests, compares *all other bytes exactly*, traverses parsed JSON with structural/type checks, and validates packed record identities and decoded normal changes. Unknown fields, new HTML changes, altered part identities, excessive drift, unexpected record counts or mutated originals return `FAIL_UNCLASSIFIED` (exit 2). An explicitly classified drift returns a successful *diagnostic* with `parity: FAIL`, `release: HOLD`. Only identical bytes may return `parity: PASS`.

Ten adversarial stdlib tests cover valid bounded drift, exact match, injected code outside payload, nonnumeric changes, overflow, changed packed identities, invalid records and source-identity tampering. This is a **diagnostic allowlist for this pinned source and these three pages only**, never a global acceptable-tolerance policy.

## Next gate

Run the exact-root independent GitHub Actions Ω10B workflow and inspect the original evidence files. If successful, proceed to isolate the generating operation for folded-octahedral tie behavior, test browser visual/occlusion parity at adversarial camera angles, and compare original macOS and Ubuntu environment/library versions. No live host or upstream source mutation.
