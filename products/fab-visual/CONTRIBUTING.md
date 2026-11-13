# Contributing to FAB.VISUAL

## Changes

Supply a focused PR with: source and license pedigree, explicit claim boundary, testable behavior, regression tests, no unexpected host mutation, model/renderer correspondence checks, and a clear outstanding-evidence list. Run `npm test` (or `node --test tests/*.test.mjs`).

## Coding

Use dependency-free Node 20.10+ ESM for the reference core. Keep geometry/adapters isolated from domain authority and release policy. Do not introduce network I/O, arbitrary evaluation, privileged headless browser operations or automatic GitHub deployment into the reference CLI.

## Versioning

SemVer pre-releases until first defended v1.0. Public source changes do not modify canonical private Drive corpus. Release requires a numbered handoff, test receipts and a positive independent authorization gate.
