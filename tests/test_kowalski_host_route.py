"""FDF/EK-002: host-bound source scope and operator law tests, no real IDE."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.fdf_host_projectdna import build_host_binding
from tools.fdf_kowalski_host_route import plan_for_host

SHA = "a" * 40


class HostBoundKowalskiBridge(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "AGENTS.md").write_text("HOST_POLICY_PRIVATE_DO_NOT_LEAK")
        (self.root / "index.html").write_text('<button><svg></svg></button>')

    def route(self, framework="react", intent="motion-build", operator="NEXT(UX)", explicit=False):
        return plan_for_host(self.root, SHA, framework, intent, operator, explicit=explicit)

    def test_valid_host_precheck_emits_reference_only(self):
        r = self.route()
        self.assertEqual(r["status"], "REFERENCE_SELECTED_HOST_PRECHECK_ONLY")
        self.assertEqual(r["host_projectdna_admission"],
                         "SCOPED_PRECHECK_COMPLETE_HOST_MASTER_REVIEW_REQUIRED")
        self.assertEqual([v["id"] for v in r["skill_route"]["selected"]],
                         ["animate", "animation-performance"])
        self.assertEqual(r["coverage_admission"], "PASS_SCOPED")
        self.assertEqual(r["mode"], "PROPOSE_ONLY")
        self.assertEqual(r["release"], "HOLD")

    def test_no_authority_promotion(self):
        r = self.route()
        for flag in ("operator_is_authenticated", "actual_ide_executed",
                     "host_policy_semantics_checked", "owner_authorized",
                     "writes_performed", "dependencies_installed",
                     "upstream_source_downloaded", "framework_claim_verified",
                     "fdf_commit_verified_by_tool"):
            self.assertFalse(r[flag], flag)

    def test_no_host_secrets_in_receipt(self):
        (self.root / ".env").write_text("DO_NOT_READ_SECRET_CONTENT")
        s = json.dumps(self.route())
        self.assertNotIn("HOST_POLICY_PRIVATE_DO_NOT_LEAK", s)
        self.assertNotIn("DO_NOT_READ_SECRET_CONTENT", s)
        self.assertNotIn(str(self.root), s)

    def test_no_caller_source_writes(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        self.route()
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir() if p.is_file()})

    def test_forbidden_operators_dont_scan(self):
        for op in ("CONTINUE()", "PUBLISH()", "DEPLOY()", "NEXT_AND_EDIT", "CHECK(ALL)", "STATUS()"):
            with self.subTest(op=op), patch("tools.fdf_kowalski_host_route.build_host_binding") as b:
                r = self.route(operator=op)
                self.assertEqual(r["status"], "HOLD_HOST_OPERATOR_NOT_DESIGN_PROPOSAL")
                b.assert_not_called()

    def test_read_only_refine_and_review(self):
        for op in ("REVIEW()", "REFINE()", "NEXT(UX@reader-architecture)"):
            with self.subTest(op=op):
                self.assertEqual(self.route(operator=op)["status"],
                                 "REFERENCE_SELECTED_HOST_PRECHECK_ONLY")

    def test_unreadable_policy_cannot_promote(self):
        (self.root / "AGENTS.md").unlink()
        r = self.route()
        self.assertEqual(r["status"], "HOLD_HOST_PROJECTDNA_PRECHECK")
        self.assertEqual(r["host_projectdna_admission"], "HOLD_HOST_POLICY_DISCOVERY_UNKNOWN")
        self.assertIsNone(r["skill_route"])

    def test_incomplete_source_coverage_blocks(self):
        (self.root / "oversize.css").write_bytes(b"x"*65537)
        r = self.route()
        self.assertEqual(r["status"], "HOLD_HOST_PROJECTDNA_PRECHECK")
        self.assertEqual(r["coverage_admission"], "HOLD_INCOMPLETE")

    def test_explicit_only_requires_user_flag(self):
        self.assertEqual(self.route(intent="prototype-variants")["status"],
                         "HOLD_EXPLICIT_USER_INVOCATION")
        r = self.route(intent="prototype-variants", explicit=True)
        self.assertEqual(r["status"], "REFERENCE_SELECTED_HOST_PRECHECK_ONLY")
        self.assertFalse(r["owner_authorized"])

    def test_framework_boundaries(self):
        self.assertEqual(self.route("react", "expo-motion-build")["status"],
                         "HOLD_FRAMEWORK_MISMATCH")
        self.assertEqual(self.route("unknown", "motion-build")["status"],
                         "HOLD_PROJECT_CONTEXT")

    def test_corrupt_previous_host_receipt_fails_closed(self):
        old = build_host_binding(self.root, SHA)
        forged = copy.deepcopy(old)
        forged["owner_authorized"] = True
        with self.assertRaisesRegex(ValueError, "stale or forged"):
            plan_for_host(self.root, SHA, "react", "motion-build",
                          previous_host_receipt=forged)

    def test_stale_host_receipt_fails_closed(self):
        old = build_host_binding(self.root, SHA)
        (self.root / "index.html").write_text("<img alt='ok'>")
        with self.assertRaisesRegex(ValueError, "stale or forged"):
            plan_for_host(self.root, SHA, "react", "motion-build",
                          previous_host_receipt=old)

    def test_valid_previous_host_receipt_accepted_but_not_authorized(self):
        old = build_host_binding(self.root, SHA)
        r = plan_for_host(self.root, SHA, "react", "motion-build",
                          previous_host_receipt=old)
        self.assertEqual(r["host_projectdna_receipt_sha256"], old["receipt_sha256"])
        self.assertFalse(r["actual_ide_executed"])

    def test_pin_mismatch_refused(self):
        with self.assertRaisesRegex(ValueError, "exact"):
            plan_for_host(self.root, "main", "react", "motion-build")
        old = build_host_binding(self.root, SHA)
        with self.assertRaisesRegex(ValueError, "stale FDF"):
            plan_for_host(self.root, "b"*40, "react", "motion-build",
                          previous_host_receipt=old)

    def test_cli_no_edit(self):
        run = subprocess.run([sys.executable, "tools/fdf_kowalski_host_route.py",
                              "--project", str(self.root), "--fdf-sha", SHA,
                              "--framework", "react", "--intent", "motion-build"],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["release"], "HOLD")
        self.assertFalse(json.loads(run.stdout)["actual_ide_executed"])

if __name__ == "__main__":
    unittest.main()
