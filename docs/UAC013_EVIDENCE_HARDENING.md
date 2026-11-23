# FDF/UAC-013 — evidence intake parser hardening

Date: **2026-11-23**. Bounded source mutation to existing stacked **DRAFT PR #16** only. The original UAC-012 source baseline is commit `8020ebb179c7493378a85432f7d7dffb6640a7d4` (257 CI tests on Ubuntu). This change is **not** a new owner-IDE activation or release.

## Source-grounded defect

Original `tools/fdf_host_evidence.py` assessed `observation["host"]` with set membership without type-checking it. JSON accepts arrays/objects, which are unhashable in Python, so a malformed `host` could raise uncaught `TypeError` rather than return a controlled HOLD. Standard `json.loads` accepted duplicate keys (ambiguous evidence) and non-finite numbers (not strict JSON); a non-UTF8 input or an unserializable directly-supplied witness could also escape the expected error boundary.

## Corrective refabrication

- Check `host` is a string **before** membership in supported host names.
- Refuse duplicate JSON object members, including nested duplicates.
- Refuse non-finite numeric JSON tokens such as NaN/Infinity.
- Convert invalid witness serialization (unserializable Python value, invalid Unicode) to fail-closed HOLD.
- CLI catches Unicode, TypeError and recursion failures in addition to prior parsing/file errors.
- Retain all existing output claim boundaries: `live_skill_activation_independently_confirmed=false`, `owner_approval_authenticated=false`, `permission_to_install=false`, `permission_to_merge=false`, `permission_to_deploy=false`, `release=HOLD`.

## Regressions and scope

Existing four GitHub tests are preserved; eighteen new adversarial cases cover unhashable host values, duplicate/nested JSON keys, non-finite numbers, UTF8, non-object/big/symlinked files, bad witness structures, forged owner/reviewer fields, invalid skill identifiers, and omitted evidence flags. The separate Linux/Windows workflow runs this expanded 22-test file; Windows symlink test is intentionally skipped due to privileges.

**Not closed:** A self-consistent hash is not a signature; local JSON can be forged, host activation needs independent actual-IDE evidence, and `read_json` symlink checks do not establish race freedom or Windows reparse/junction containment. Exact original standalone fourteen-test ZIP from Oct 21 is **not mounted in the present runtime**. This is new reviewed-branch coverage, **not** a claim that the old portable package's source/manifest or entire fourteen-test suite was reimported.

## Release protection

Do not copy external skill instruction bodies, alter root project policies, merge or deploy. Keep the existing PR #16 draft, preserve the last-green source SHA, and require independent reviewer and owner-native evidence before promotion. This patch qualifies parser robustness only; actual local FDF skill activation and protected main remain HOLD.
