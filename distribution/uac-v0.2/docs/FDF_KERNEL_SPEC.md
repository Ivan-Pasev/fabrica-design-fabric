# FDF() Kernel Contract · UAC-002

Version 0.2, 18 October 2026.

### Inputs
- true active workspace (provided by authorized IDE owner), platforms selected from supported adapters, lifecycle indicators, bounded root policies, optional verified host instructions and current task;
- first-party skill catalog with original skill bodies, licensed pinned upstream references (not executed), root-hook preference and exact owner-reviewed plan hash.

### State machine
`UNINITIALIZED → OBSERVED → FIT_PLAN → REVIEW_PENDING → ADDITIVE_INSTALLED → HASH_VERIFIED → HOST_ACTIVATION_UNVERIFIED → GUIDED_EVOLUTION`.

No transition from `REVIEW_PENDING` to installation without exact plan SHA *and* separate host-native owner authorization. No `GUIDED_EVOLUTION` step implies write authority. `HOLD` is the default outcome when conflict, missing source, missing policy authority or non-verifiable host state exists.

### ProjectDNA
Static bounded source signals, observed root policy file hashes/entry counts, technology hints and Git working-tree status. It does not interpret semantic priority, discover all nested/global policies, run package scripts or verify actual IDE behavior. Do not print secret file contents.

### Kernel mode
`AUGMENT_EXISTING_UNVERIFIED` when known root instruction/orchestration surfaces are detected; preserve and only add pointers at separately approved scope. Otherwise `SCAFFOLD_ADVISORY_KERNEL`; this does not prove no global instruction hierarchy exists.

### First-party skill selection
Universal project-observer, governance-gate, evolution-planner and verification-engine. Fit-scored design-critic/accessibility-review/motion-director for UI signals; runtime-architecture for software stack; research-provenance for explicit research directory hints. Unselected skill bodies are not installed. All selected skills have host-discoverable frontmatter. Third-party upstream is reference-only.

### Platform adapters
Codex/Antigravity share `.agents/skills`; Antigravity rule requires valid `trigger: model_decision`, no legacy workflows; Cursor `.cursor/rules/*.mdc`; Gemini CLI `.gemini/skills`; ChatGPT Project and AI Studio manual instructions. A generated file is not proof the host loaded its instructions.

### Security / rollback
Plan SHA locks the source-observed plan, is **not** a signature of owner identity. An `apply` failure may leave review-required partial side effects due to OS concurrency/TOCTOU; script makes best-effort rollback. `verify` compares content hashes. `rollback` refuses changed managed files and preserves original root-byte context in controlled fixtures. Continuous upgrades require separate versioned migration review; v0.2 does not auto-update old installations or self-evolve kernels.

### Actual host admission gates
- real project/open IDE identity, global/nested policy readback, selected skill activation, user review of candidate files, actual permission receipt, source/build/functional checks and independent reviewer as needed;
- GitHub review and protected-main enforcement remain external; local test PASS does not imply release PASS.
