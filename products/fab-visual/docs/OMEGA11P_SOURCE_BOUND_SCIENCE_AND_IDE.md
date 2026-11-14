# FAB.VISUAL Ω11P — Source-Bound Quantitative Evidence and Controlled IDE Packaging

**Source:** Public first-party `Ivan-Pasev/fabrica-design-fabric` experimental branch `feature/fab-visual-omega11p-bound-science-ide-package`, stacked on Ω11O draft PR #40 at SHA `42e960f85ee5a796d5d4e7da52209c0a45de5dda`. **Candidate:** v0.10.0-alpha.0. **Rights:** original first-party source MIT; Anatomy original MIT five-blob subset unchanged; original upstream `1482e8469b0a9e0d8cc18ea2740a01423d29ae80` (173 objects). **Production release HOLD.**

## 1. Original source vs actual new implementation

The existing Ω11O sidecar validates SI dimensions and signed numerical balance but had no cryptographic coupling to a real SceneIR. Ω11P introduces `src/visual/bound-quantitative.mjs` and `fixtures/bound-microgrid.synthetic.json` with an explicitly trusted original `fab.scene.v0.2` input. The bound envelope requires an exact `sha256:` of `canonicalJSON(scene)`, source scene ID, source model ID/revision, representation and a source-labelled quantitative model. Any changed original model authority, status, coordinate, topology, source observable or revision changes the digest and causes an exception before any nominal/interval result. This is byte-content correspondence with the separately supplied trusted source, NOT third-party publisher authentication or empirical measurement provenance.

### Core typed envelope

```json
{
  "schema": "fab.visual.bound-quantitative.v1",
  "scope": "SOURCE_LOCKED_INTERNAL_CONSISTENCY_ONLY",
  "sourceSceneDigest": "sha256:9ae22ab08570d4ea8164c1246c712381c5ba5d063eb057e8b99e15b6c6a0c53e",
  "sourceSceneId": "citizen-solar-illustrative-microgrid",
  "sourceModel": {"id":"fab.visual.omega11l.energy","revision":"0.6.0-alpha.0"},
  "sourceRepresentation": "ANALOGICAL",
  "quantitative": "exact embedded fab.visual.quantitative.v1 object from synthetic fixture",
  "readouts": "source part/link counts or source-declared numeric observable comparisons"
}
```

The `quantitative` and `readouts` keys above are explanatory placeholders only; the checked executable JSON fixture has their full typed values. A user must not paste the shortened presentation as an executable schema.

### Scope of source-bound evaluators

`PART_COUNT` and `LINK_COUNT` are directly evaluated from the actual separately loaded SceneIR structure and are genuine independent *structural* counts. `NUMERIC_SOURCE_OBSERVABLE` is only a value read from the source's named observable, *not* an independently executed model solver; the report explicitly marks `DECLARED_SOURCE_VALUE_COMPARISON_NOT_INDEPENDENT_MODEL_EVALUATION`. No inferred sensor reading or unverified PHYSICAL source is promoted.

## 2. Mathematical uncertainty distinction

The inherited Ω11O nominal numeric audit returns PASS when `|Σ sign_i × q_i × SI_factor_i| ≤ max(absoluteTolerance_SI, relativeTolerance × Σ |q_i SI_factor_i|)`. Ω11P constructs a **binary64 outward-rounded term interval** for each declared `q_i ± uncertainty_i`, converts by its declared positive SI factor and adds via outward-rounded float operations. It classifies the interval relative to the declared tolerance ±τ:

- `WITHIN_DECLARED_BOUNDS`: the entire computed interval lies inside the tolerance band.
- `OUTSIDE_DECLARED_BOUNDS`: the computed interval is disjoint from that band.
- `INCONCLUSIVE_OVERLAP`: some values lie within and others outside the tolerance.

Crucially, decimal input interpretation, calibrated instrument error and true physical-state uncertainty are **NOT_CERTIFIED**. The interpreter uses supplied IEEE-754 numbers and declared uncertainty only; it is not an independently formalized real-number interval-arithmetic proof. No independence assumptions, covariance assumptions or statistical confidence claims are made. A zero nominal residual is not a robust PASS if its uncertainty interval overlaps a boundary.

**Synthetic fixture actual expected result:** nominal `PASS`, interval classifications `INCONCLUSIVE_OVERLAP` for both the power bus and the energy window; aggregate result `INCONCLUSIVE` with CLI exit 2 and release HOLD. Setting declared uncertainties to 0 in a test can yield `WITHIN_DECLARED_BOUNDS` PASS for the declared arithmetic, *not physics*.

## 3. Exact executable commands and output

```bash
cd products/fab-visual
node --test tests/*.test.mjs
node bin/fab-visual.mjs audit-bound templates/energy-microgrid.scene.json fixtures/bound-microgrid.synthetic.json
node bin/fab-visual.mjs ide-package --dry-run /path/to/existing-parent/new-skill
# ONLY after explicit user authorization and checking the dry-run files:
node bin/fab-visual.mjs ide-package --write /path/to/existing-parent/new-skill
```

`audit-bound` uses the original untouched SceneIR and bounded JSON sidecar, outputs a machine-readable `fab.visual.bound-quantitative-report.v1` receipt, and returns exit 2 on FAIL or INCONCLUSIVE. Even arithmetic PASS outputs `physicalValidation: NOT_RUN`, `formalProof: NOT_RUN`, `externalSourceAuthentication: NOT_PRESENT`, `hostAuthorization: NOT_RUN`, `release: HOLD`.

## 4. IDE skill package security and capabilities

The first-party `src/ide/ide-package.mjs` selects exactly five whitelisted source-reference files: root IDE entrypoint, portable SKILL.md, machine-readable capability manifest, product constitution and pinned Anatomy source lock. A dry-run reads them and calculates SHA-256 without filesystem writes. `--write` is a separately intentional user command creating a previously absent sibling directory after path, ancestor symlink, collision and source-tree checks; the output includes a package evidence JSON and no executable runtime. The code does not clone GitHub, install dependencies, fetch untrusted code or change host configuration. It does not prove that an external IDE will auto-register or execute the skill; host-native installation and permission checks remain a separate review.

Security bounds: refuse missing parent, NUL path, repository source-tree destination, symlink ancestor or destination, existing target and unknown mode. An adversarial multi-user filesystem race or privilege boundary is not independently certified; do not run as root or target shared untrusted writable directories. No secrets, remote shell execution or automatic host edits.

## 5. Failure and proof obligations

Negative tests cover stale SHA/model ID or revision, modified topology and original claims/authority, wrong dimensional units, bogus source observable, synthetic input mislabelled as real measurement, missing/forged readout evaluator, duplicate IDs, double-signed negative flow, invalid numeric uncertainty, nominal/interval contradiction, unsafe IDE target paths, symlinks, overwrite attempts, and forged CLI flags. Original MIT Anatomy source, its five hash-locked objects and 173 upstream Git source blobs stay immutable.

## 6. Deliberate deferred work

- The existing strict **six-entry local project ZIP** remains unchanged. Adding optional quantitative evidence to ZIP requires a separate versioned archive ABI, signed source hash and backward compatibility tests, so it is NOT_IMPLEMENTED in Ω11P.
- A true independently executed domain model evaluator, timestamped/calibrated instrument attestation, decimal-exact or Lean-proved interval bounds, full original upstream Anatomy geometric audit, real rendering/GPU frame proof and runtime IDE auto-registration are **NOT_RUN**.
- Production host deployment, database schema migration, main merge, data authorization and scientific admission remain **HOLD**.

## 7. Acceptance receipt

Initial Ω11P source-locked GitHub Actions run #43623286387 at preliminary branch head succeeded: **273/273 Node tests**, source lock, three-domain real Chromium Studio/Gallery/ZIP regressions, bounded SHA scene audit and zero-write IDE plan. Final exact documentation-head and independent PR CI receipts must be verified and appended before closure; a prior green CI is not evidence for a newer commit.