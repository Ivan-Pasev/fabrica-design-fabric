#!/usr/bin/env bash
set -euo pipefail
# Explicit maintainer-operated acquisition. Does not execute untrusted browser tools.
commit='1482e8469b0a9e0d8cc18ea2740a01423d29ae80'
root="${1:-vendor/anatomy}"
if [[ -e "$root" ]]; then echo "Target exists; refusing overwrite: $root" >&2; exit 2; fi
git clone --no-checkout https://github.com/wheresryan22/anatomy.git "$root"
git -C "$root" checkout --detach "$commit"
actual="$(git -C "$root" rev-parse HEAD)"
[[ "$actual" == "$commit" ]] || { echo "Commit mismatch" >&2; exit 2; }
grep -q 'MIT License' "$root/LICENSE"
printf 'Pinned Anatomy at %s\n' "$actual"
echo 'Source acquired only; complete audit, license review and isolated browser tests remain mandatory.'
