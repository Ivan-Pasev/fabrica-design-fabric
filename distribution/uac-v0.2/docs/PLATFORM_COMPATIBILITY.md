# Source-checked host adapter matrix (18 October 2026)

| Host | Installed workspace artifact | Runtime validation needed |
| --- | --- | --- |
| Codex | Optional root `AGENTS.md` hook; `.agents/skills/{selected}/SKILL.md` | Check actual Codex session discovered applicable context and skills |
| Cursor | `.cursor/rules/fabrica-design-fabric.mdc` | Inspect rule list/activation under current IDE settings |
| Antigravity IDE/CLI | `.agents/rules/fabrica-design-fabric.md` (`trigger: model_decision`); `.agents/skills/{selected}` | Inspect actual Customizations/skills activation; no `.agents/workflows` artifacts |
| Gemini CLI | `.gemini/skills/{selected}` and optional root `GEMINI.md` | `gemini skills list`/reload and actual skill activation if owner permits |
| ChatGPT Project | Manual `.fabrica/CHATGPT_FDF_INJECTION.md` and project sources | Owner pastes into actual Project settings; cannot be installed through local file writes |
| Google AI Studio | Manual `.fabrica/AISTUDIO_FDF_INJECTION.md` | Owner imports/syncs allowed GitHub repo in Build; review prompt and code/diff |

Antigravity workflow retirement is announced **October 19, 2026**; v0.2 removes the v0.1 generated legacy workflow. See https://www.antigravity.google/docs/migration/workflows-to-skills/ and https://www.antigravity.google/docs/rules/ .

Sources:
- https://developers.openai.com/blog/skills-agents-sdk
- https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide
- https://docs.cursor.com/context/rules-for-ai
- https://www.antigravity.google/docs/rules/
- https://antigravity.google/docs/skills
- https://geminicli.com/docs/cli/gemini-md/
- https://geminicli.com/docs/cli/skills/
- https://help.openai.com/en/articles/10169521-projects-in-chatgpt
- https://ai.google.dev/gemini-api/docs/aistudio-build-mode

Upstream documentation reflects source-observed surfaces, not local runtime verification. Host instruction precedence and user approval govern every action.
