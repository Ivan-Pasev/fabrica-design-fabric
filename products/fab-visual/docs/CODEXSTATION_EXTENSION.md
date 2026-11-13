# CodexStation universal FAB.VISUAL extension profile

## Requirement

A single portable capability should work as an *additive overlay* in multiple CodexStation releases, preserving their different source roots, constitutional rules and existing tools.

## Compatibility contract

Input: `codexstation_root` absolute existing directory and separately read current local START/CONSTITUTION/AGENTS/STATE. Output: dry-run intent, then if explicitly instructed `--apply` a new `.agents/skills/fab-visual/SKILL.md` plus `.codexstation/extensions/fab-visual/` runtime and receipt. No root-level AGENTS override, no tools registry mutation, no network changes. A collision produces HOLD; a different host should use host-native policy adapters reviewed separately.

## Supported distribution intent

- Codex/Antigravity/OpenCode-compatible Agent Skill folder: primary implemented route.
- Claude-compatible skill routing: package can be copied according to host conventions, but not claimed installed.
- ChatGPT plugin/MCP bridge: planned only. Requires connector-specific tool permissions and a server API with human consent.
- All CodexStation Ω/Perplexity/Antigravity/MLCO/HighestOne carriers: architectural portability candidate, **not tested against actual releases**.

## Source-of-authority order

Deployment live constitutional control > attached FAB.VISUAL install receipt > public reference API > cached summaries. In all hosts, `MODEL != REALITY`, `SKILL != AUTHORITY`, `CLAIM != EVIDENCE`, `AVAILABLE != AUTHORIZED`.

## Uninstall

Installer creates only self-contained new paths; removal must be reviewed against the receipt and the current host before deleting them. No destructive uninstall is bundled.
