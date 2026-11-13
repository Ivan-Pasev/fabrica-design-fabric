# FAB.VISUAL Portable CodexStation Extension

## Safe preview

`node scripts/install-codexstation.mjs --root /absolute/path/to/existing/codexstation`

## Explicit opt-in

`node scripts/install-codexstation.mjs --root /absolute/path/to/existing/codexstation --apply`

Only creates `.agents/skills/fab-visual` and `.codexstation/extensions/fab-visual`; existing collisions fail closed. Does not override any station policy, credential, memory, tool authorization, deployment, GitHub repo or Google Drive document. Verify target identity and current constitution before any installation.

## Post-install synthetic demo

`node .codexstation/extensions/fab-visual/bin/fab-visual.mjs demo /tmp/fab-visual-policy.html`

Tests were executed on a temporary folder, not a live CodexStation release. The independently verifiable **MIT-licensed pinned Anatomy subset** is now installed under `vendor/anatomy`; the complete upstream repository is not included. After installation run `node .codexstation/extensions/fab-visual/bin/fab-visual.mjs anatomy-verify` and `node .codexstation/extensions/fab-visual/bin/fab-visual.mjs anatomy-timeline /tmp/fab-visual-anatomy.html`.
