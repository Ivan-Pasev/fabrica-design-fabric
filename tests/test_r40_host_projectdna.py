"""R40 host authority precheck: real fixture files, no authority promotion."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.fdf_host_projectdna import build_host_binding, verify_host_binding

SHA = "490493bf9aeae44302d074a601b20057c04f4575"


class HostAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "AGENTS.md").write_text("HOST RULES: keep scientific claims intact")
        (self.root / "index.html").write_text('<main><img data-note="alt=spoof" src="a"></main>')

    def receipt(self):
        return build_host_binding(self.root, SHA)

    def test_binds_real_policy_sha_and_scoped_source(self):
        r = self.receipt()
        self.assertEqual(r["admission"], "SCOPED_PRECHECK_COMPLETE_HOST_MASTER_REVIEW_REQUIRED")
        self.assertEqual(r["policy_files"][0]["sha256"], hashlib.sha256(b"HOST RULES: keep scientific claims intact").hexdigest())
        self.assertEqual(r["coverage_admission"], "PASS_SCOPED")
        self.assertEqual(r["candidate_ui_findings"], 1)
        self.assertEqual(r["ui_observed_files"], 1)
        self.assertEqual(verify_host_binding(self.root, r), r)

    def test_policy_content_never_emitted(self):
        (self.root / "AGENTS.md").write_text("HOST_PRIVATE_RULE_VALUE_ONLY_IN_FILE")
        (self.root / ".env").write_text("HOST_PRIVATE_SECRET_ONLY_IN_FILE")
        raw = json.dumps(self.receipt())
        self.assertNotIn("HOST_PRIVATE_RULE_VALUE_ONLY_IN_FILE", raw)
        self.assertNotIn("HOST_PRIVATE_SECRET_ONLY_IN_FILE", raw)

    def test_host_semantics_and_authorization_not_promoted(self):
        r = self.receipt()
        self.assertFalse(r["owner_authorized"])
        self.assertFalse(r["automated_edits"])
        self.assertFalse(r["fdf_commit_verified_by_tool"])
        self.assertEqual(r["host_master_authority"], "REQUIRES_ACTUAL_IDE_AGENT_REVIEW")
        self.assertEqual(r["real_caller_ide_witness"], "NOT_VERIFIED")
        self.assertEqual(r["runtime_checks_executed"], [])
        self.assertEqual(r["release"], "HOLD")

    def test_policy_change_invalidates_receipt(self):
        old = self.receipt()
        (self.root / "AGENTS.md").write_text("CHANGED")
        with self.assertRaisesRegex(ValueError, "stale or forged"):
            verify_host_binding(self.root, old)

    def test_ui_change_invalidates_receipt(self):
        old = self.receipt()
        (self.root / "index.html").write_text('<img alt="actual">')
        with self.assertRaisesRegex(ValueError, "stale or forged"):
            verify_host_binding(self.root, old)

    def test_forged_permission_claim_denied(self):
        fake = copy.deepcopy(self.receipt())
        fake["owner_authorized"] = True
        with self.assertRaisesRegex(ValueError, "stale or forged"):
            verify_host_binding(self.root, fake)

    def test_bad_pin_denied(self):
        for sha in ("main", "z" * 40, "1234", SHA.upper(), ""):
            with self.subTest(sha=sha), self.assertRaisesRegex(ValueError, "exact"):
                build_host_binding(self.root, sha)

    def test_absent_known_root_policies_holds(self):
        (self.root / "AGENTS.md").unlink()
        r = self.receipt()
        self.assertEqual(r["admission"], "HOLD_HOST_POLICY_DISCOVERY_UNKNOWN")
        self.assertEqual(r["policy_files"], [])

    def test_symlink_policy_not_followed(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "policy.md"
            target.write_text("PRIVATE_OUTSIDE")
            (self.root / "AGENTS.md").unlink()
            (self.root / "AGENTS.md").symlink_to(target)
            r = self.receipt()
            self.assertEqual(r["admission"], "HOLD_POLICY_UNREADABLE")
            self.assertEqual(r["policy_files"][0]["status"], "HOLD_SYMLINK")
            self.assertNotIn("PRIVATE_OUTSIDE", json.dumps(r))

    def test_oversized_policy_holds(self):
        (self.root / "AGENTS.md").write_bytes(b"p" * 65537)
        self.assertEqual(self.receipt()["admission"], "HOLD_POLICY_UNREADABLE")

    def test_incomplete_source_coverage_holds(self):
        (self.root / "bad.css").write_bytes(b"x" * 65537)
        self.assertEqual(self.receipt()["admission"], "HOLD_SOURCE_COVERAGE")

    def test_no_ui_source_is_not_ready(self):
        (self.root / "index.html").unlink()
        self.assertEqual(self.receipt()["admission"], "HOLD_NO_UI_FILES_OBSERVED")

    def test_digests_include_allowlisted_second_policy(self):
        (self.root / ".github").mkdir()
        (self.root / ".github/copilot-instructions.md").write_text("own policy")
        r = self.receipt()
        self.assertEqual({x["path"] for x in r["policy_files"]}, {"AGENTS.md", ".github/copilot-instructions.md"})
        self.assertEqual(verify_host_binding(self.root, r), r)

    def test_cli_no_project_writes(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        cmd = [sys.executable, "tools/fdf_host_projectdna.py",
               "--project", str(self.root), "--fdf-sha", SHA]
        p = subprocess.run(cmd, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(p.stdout)["mode"], "PROPOSE_ONLY")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir() if p.is_file()})

    def test_cli_verify_rejects_policy_staleness(self):
        r = self.receipt()
        with tempfile.TemporaryDirectory() as td:
            receipt_path = Path(td) / "receipt.json"
            receipt_path.write_text(json.dumps(r))
            (self.root / "AGENTS.md").write_text("changed")
            cmd = [sys.executable, "tools/fdf_host_projectdna.py",
                   "--project", str(self.root), "--fdf-sha", SHA, "--verify", str(receipt_path)]
            p = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("stale or forged", p.stderr)


if __name__ == "__main__":
    unittest.main()
