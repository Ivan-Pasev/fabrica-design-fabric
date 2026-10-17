"""R42 fail-closed compatibility tests; synthetic input, no real host IDE."""
import json
import subprocess
import sys
import unittest
from tools.fdf_host_operator_gate import evaluate

SHA = "a" * 40


def case(operator, pending=None, accepted=None, host_sha=SHA):
    return {"operator": operator, "host_sha": host_sha,
            "pending": pending, "accepted_proposal_id": accepted}


class OperatorPrecedenceTests(unittest.TestCase):
    def test_known_readonly_operators(self):
        for op in ("STATUS()", "NEXT()", "NEXT(UI)", "NEXT(UX@reader-architecture)",
                   "CHECK(ALL)", "REVIEW()", "REFINE()"):
            with self.subTest(op=op):
                r = evaluate(case(op))
                self.assertEqual(r["verdict"], "HOST_READ_ONLY_OPERATOR")
                self.assertFalse(r["host_mutation_authorized"])
                self.assertFalse(r["host_mutation_executed"])

    def test_continue_without_pending_holds(self):
        self.assertEqual(evaluate(case("CONTINUE()"))["verdict"],
                         "HOLD_NO_CURRENT_ACCEPTED_PROPOSAL")

    def test_continue_with_unaccepted_proposal_holds(self):
        p = {"id": "U1", "host_sha": SHA, "scope": ["theme.css"]}
        self.assertEqual(evaluate(case("CONTINUE()", p))["verdict"],
                         "HOLD_NO_CURRENT_ACCEPTED_PROPOSAL")

    def test_continue_wrong_id_holds(self):
        p = {"id": "U1", "host_sha": SHA, "scope": ["theme.css"]}
        self.assertEqual(evaluate(case("CONTINUE()", p, "U2"))["verdict"],
                         "HOLD_STALE_OR_UNACCEPTED_PROPOSAL")

    def test_continue_wrong_sha_holds(self):
        p = {"id": "U1", "host_sha": SHA, "scope": ["theme.css"]}
        self.assertEqual(evaluate(case("CONTINUE()", p, "U1", "b" * 40))["verdict"],
                         "HOLD_STALE_OR_UNACCEPTED_PROPOSAL")

    def test_continue_valid_candidate_is_not_authorization(self):
        p = {"id": "U1", "host_sha": SHA, "scope": ["src/theme.css"]}
        r = evaluate(case("CONTINUE()", p, "U1"))
        self.assertEqual(r["verdict"], "HOST_CONTINUE_PREFLIGHT_ONLY")
        self.assertFalse(r["host_mutation_authorized"])
        self.assertFalse(r["host_mutation_executed"])
        self.assertEqual(r["release"], "HOLD")

    def test_no_release_operator_granted(self):
        for op in ("PUBLISH()", "DEPLOY()"):
            with self.subTest(op=op):
                r = evaluate(case(op))
                self.assertTrue(r["verdict"].startswith("HOLD_"))
                self.assertFalse(r["host_mutation_authorized"])

    def test_unknown_operator_holds(self):
        self.assertEqual(evaluate(case("NEXT_AND_EDIT"))["verdict"], "HOLD_UNKNOWN_OPERATOR")

    def test_invalid_operator_shape(self):
        with self.assertRaises(ValueError):
            evaluate({"operator": "NEXT()"})

    def test_traversal_holds(self):
        for bad in ("../secret", "/root/a", "src\\secret", "~/secret", "src/../../a"):
            with self.subTest(bad=bad):
                p = {"id": "U1", "host_sha": SHA, "scope": [bad]}
                self.assertEqual(evaluate(case("CONTINUE()", p, "U1"))["verdict"],
                                 "HOLD_INVALID_PROPOSAL_PATH")

    def test_duplicate_scope_holds(self):
        p = {"id": "U1", "host_sha": SHA, "scope": ["page.tsx", "page.tsx"]}
        self.assertEqual(evaluate(case("CONTINUE()", p, "U1"))["verdict"],
                         "HOLD_DUPLICATE_SCOPE")

    def test_empty_and_excessive_scope_holds(self):
        for scope in ([], [f"a/{i}.tsx" for i in range(13)]):
            p = {"id": "U1", "host_sha": SHA, "scope": scope}
            self.assertEqual(evaluate(case("CONTINUE()", p, "U1"))["verdict"],
                             "HOLD_SCOPE_UNKNOWN_OR_EXCESSIVE")

    def test_cli_readonly_proposal(self):
        payload = json.dumps(case("NEXT(UX)"))
        run = subprocess.run([sys.executable, "tools/fdf_host_operator_gate.py"],
                             input=payload, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["verdict"], "HOST_READ_ONLY_OPERATOR")

    def test_cli_rejects_bad_json(self):
        run = subprocess.run([sys.executable, "tools/fdf_host_operator_gate.py"],
                             input="{invalid", text=True, capture_output=True)
        self.assertNotEqual(run.returncode, 0)

    def test_documentation_has_no_old_self_authorizing_sentence(self):
        from pathlib import Path
        guide = Path("IDE_MASTER_INJECTION.md").read_text("utf-8")
        self.assertNotIn("this prompt authorizes the host to", guide)
        self.assertIn("this injection prompt does not itself authorize", guide)
        self.assertIn("proposal-only", guide)
        self.assertIn("CONTINUE()", guide)

if __name__ == "__main__":
    unittest.main()
