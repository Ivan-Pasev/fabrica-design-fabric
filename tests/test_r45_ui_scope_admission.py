"""R45 scope admission on the EK-003-based review stack; no host IDE execution."""
import unittest
from tools.fdf_host_operator_gate import evaluate
SHA = "a"*40

def proposal(paths, op="CONTINUE()"):
    return evaluate({"operator":op, "host_sha":SHA, "accepted_proposal_id":"p1",
      "pending":{"id":"p1", "host_sha":SHA, "scope":paths}})

class R45Scope(unittest.TestCase):
    def test_ui_only_is_advisory(self):
        for path in ("src/component.tsx", "app/page.jsx", ".vitepress/theme/custom.css",
                     ".vitepress/theme/Reader.vue", "styles/main.scss", "ui/page.svelte"):
            with self.subTest(path=path):
                r=proposal([path])
                self.assertEqual(r["verdict"], "HOST_CONTINUE_PREFLIGHT_ONLY")
                self.assertFalse(r["host_mutation_authorized"])
                self.assertFalse(r["host_mutation_executed"])
                self.assertEqual(r["release"], "HOLD")
    def test_host_governance_and_ci_blocked(self):
        for path in ("AGENTS.md", "docs/AGENTS.md", "CLAUDE.md", "GEMINI.md",
                     "AI_CRITICAL.md", ".github/workflows/verify.yml",
                     ".agents/skills/agent.tsx", ".cursor/rules.css",
                     ".vitepress/config.ts", ".git/hooks/post-commit.css"):
            with self.subTest(path=path):
                self.assertEqual(proposal([path])["verdict"],"HOLD_PROTECTED_PROPOSAL_PATH")
    def test_config_and_generated_paths_blocked(self):
        for path in ("package.json", "package-lock.json", "pnpm-lock.yaml",
                     "tsconfig.json", "vite.config.ts", "next.config.mjs",
                     "dist/index.html", "build/page.css", "node_modules/thing.tsx",
                     "private/surface.vue", "src/.env.production"):
            with self.subTest(path=path):
                self.assertEqual(proposal([path])["verdict"],"HOLD_PROTECTED_PROPOSAL_PATH")
    def test_scientific_content_separate_review(self):
        for path in ("docs/fqft.md", "docs/math.mdx", "papers/part.tex",
                     "references/a.bib", "docs/article.markdown"):
            with self.subTest(path=path):
                self.assertEqual(proposal([path])["verdict"],
                                 "HOLD_CONTENT_OR_SCIENCE_REVIEW_REQUIRED")
    def test_non_ui_sources_hold(self):
        for path in ("app/data.json", "img/photo.png", "scripts/run.py", "art/icon.svg"):
            with self.subTest(path=path):
                self.assertEqual(proposal([path])["verdict"], "HOLD_OUTSIDE_UI_ONLY_SCOPE")
    def test_mixed_scope_fails_closed(self):
        r=proposal(["src/Reader.vue", "docs/theory.md"])
        self.assertEqual(r["verdict"], "HOLD_CONTENT_OR_SCIENCE_REVIEW_REQUIRED")
    def test_path_spelling_requires_canonical(self):
        for path in ("src//view.tsx", "./src/view.tsx", "src/./view.tsx",
                     "src/../view.tsx", "C:/repo/view.tsx", "src/%2e%2e/a.tsx",
                     "src\\view.tsx", "~/a.css"):
            with self.subTest(path=path):
                self.assertEqual(proposal([path])["verdict"],"HOLD_INVALID_PROPOSAL_PATH")
    def test_next_remains_read_only(self):
        r=proposal([".github/workflows/deploy.yml"],op="NEXT(UX)")
        self.assertEqual(r["verdict"],"HOST_READ_ONLY_OPERATOR")
        self.assertFalse(r["host_mutation_authorized"])
    def test_no_pending_continuation_stays_hold(self):
        r=evaluate({"operator":"CONTINUE()", "host_sha":SHA,
                    "accepted_proposal_id":None, "pending":None})
        self.assertEqual(r["verdict"],"HOLD_NO_CURRENT_ACCEPTED_PROPOSAL")

if __name__=="__main__":
    unittest.main()
