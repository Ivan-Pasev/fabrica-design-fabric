# Ω7 Constitutional principle — full upstream first

**Upstream Anatomy is the operational substrate. FAB.VISUAL only extends it.**

| Identity | Scope | Authority |
|---|---|---|
| `wheresryan22/anatomy@1482e8469b0a9e0d8cc18ea2740a01423d29ae80` | Complete original 173-blob, 27,648,351-byte Git tree | Original upstream, MIT copyright Ryan |
| `.gitmodules` + pinned gitlink | Entire upstream directory at `products/fab-visual/upstream/anatomy` | Source/availability lock only |
| `vendor/anatomy` | Four exact kit modules + original MIT LICENSE (Ω5 compatibility) | Old bounded adapter, NOT full engine |
| `src`, `scripts`, `docs`, `research`, `extensions` outside the submodule | Additive FAB.VISUAL orchestration, testing and domain semantics | FAB.SYS; cannot rewrite original source silently |

The default downstream distribution must **never advertise the old vendor subset as full Anatomy**. New installation profiles should use original upstream skill at `.agents/skills/anatomy`, including every original file, while FAB.VISUAL remains a separate skill and optional overlay. No deletion or overwrite of a host's existing Anatomy or other skill is allowed.

## Absolute invariants

- `SOURCE_ID`: Entire original 173-blob tree is identified by its exact Git commit, checked against Git commit 1482e84... AND root tree 89299cdfce386a71723a7e57bb9fe219875582fc, and by recomputing every working-tree Git blob hash. No `latest` or sliding tags in trusted builds.
- `SOURCE_COMPLETENESS`: 173 files / 27,648,351 tracked blob bytes. Includes checked-in HTML, nine printable PDF examples, React and WebGL code, 3D, tests, reference docs, CLI scripts, examples.
- `INCREMENTALITY`: No direct modification of original upstream submodule. Modifications/derivatives are opt-in outside the immutable tree and independently versioned.
- `FUNCTIONAL_PARITY`: Source completeness is necessary but not sufficient; upstream Node tests, clean light/dark rebuilds, WebGL, 3D motion, browser and PDF export have separately recorded PASS/FAIL/NOT_RUN evidence. A green source hash does not imply green rendering.
- `LICENSE`: Keep original `LICENSE`, attribution, SPDX and third-party dependency licenses. Copyright provenance is never fabricated.
- `CLAIM_BOUNDARY`: No visual, mechanical or scientific claim is elevated by geometry acceptance, screenshots or hashes alone.
- `SECURITY`: untrusted figures, PRs and third-party forks run only on isolated workers with minimal permissions; no credentials in the browser. Import external modules only after license and manifest review.
- `UPGRADE`: Pin → diff full upstream → run full parity → publish bounded additive change → version lock. Forks contribute isolated ideas, test cases and adapters, not wholesale unreviewed replacement trees.

## Acquiring the FULL original source

From the FDF repository root on a Git-enabled machine with network:

```sh
git submodule sync --recursive
git submodule update --init --recursive products/fab-visual/upstream/anatomy
node products/fab-visual/scripts/full-anatomy-source.mjs --clean
```

To execute the original Anatomy self-tests after checkout:

```sh
cd products/fab-visual/upstream/anatomy
node --test scripts/*.test.mjs
```

The original upstream CI additionally installs React, React DOM, TypeScript and esbuild in an isolated temp directory, regenerates example pages in both themes, and asserts byte-identical outputs. Follow the pinned upstream `.github/workflows/ci.yml` for those exact commands, or inspect the FAB.VISUAL Ω7 CI receipts. **Full original testing must run on the complete checkout before marking parity PASS.**

## CodexStation full-profile installation

In source checkout, from the product root:

```sh
node scripts/install-full-anatomy-codexstation.mjs --root /reviewed/codexstation
node scripts/install-full-anatomy-codexstation.mjs --root /reviewed/codexstation --apply
```

Default dry-run; `--apply` is separate opt-in and includes a clean original source tree hash review. Copies all original source files to `.agents/skills/anatomy` without modifying them; existing paths cause HOLD. A receipt is written OUTSIDE the skill files. Installed means *available, not authorized*; no full-profile installation has been approved on an actual CodexStation deployment.
