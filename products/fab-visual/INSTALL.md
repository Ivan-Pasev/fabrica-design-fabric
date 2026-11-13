# FAB.VISUAL Portable CodexStation Extension

## Safe preview

`node scripts/install-codexstation.mjs --root /absolute/path/to/existing/codexstation`

## Explicit opt-in

`node scripts/install-codexstation.mjs --root /absolute/path/to/existing/codexstation --apply`

Only creates `.agents/skills/fab-visual` and `.codexstation/extensions/fab-visual`; existing collisions fail closed. Does not override any station policy, credential, memory, tool authorization, deployment, GitHub repo or Google Drive document. Verify target identity and current constitution before any installation.

## Post-install synthetic demo

`node .codexstation/extensions/fab-visual/bin/fab-visual.mjs demo /tmp/fab-visual-policy.html`

Tests were executed on a temporary folder, not a live CodexStation release. External Anatomy source is NOT included.
