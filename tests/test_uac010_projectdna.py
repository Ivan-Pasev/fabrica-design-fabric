"""UAC-010 metadata-only ProjectDNA witness regression and refusal suite."""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
import sys
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location("fdf_projectdna_local", TOOLS / "fdf_projectdna.py")
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

class ProjectDNAWitnessTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.secret = "SAMPLE PRIVATE PROJECT POLICY CONTENT -- must not be transmitted"
        (self.root / "AGENTS.md").write_text(self.secret, encoding="utf-8")
        (self.root / "package.json").write_text('{"private":true,"scripts":{"postinstall":"DO NOT RUN"}}', encoding="utf-8")
        (self.root / ".cursor" / "rules").mkdir(parents=True)
        (self.root / ".cursor" / "rules" / "design.mdc").write_text("sample cursor policy", encoding="utf-8")
    def call(self, intent="design", host="cursor"):
        return w.capture(str(self.root), host, intent)
    def test_projectdna_is_read_only(self):
        before = {p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.call()
        after = {p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
    def test_policy_content_not_disclosed(self):
        self.assertNotIn(self.secret, json.dumps(self.call()))
    def test_policy_digests_and_relative_paths(self):
        rows=self.call()["observed_policy_files"]
        self.assertIn("AGENTS.md", {r["relative_path"] for r in rows})
        self.assertIn(".cursor/rules/design.mdc", {r["relative_path"] for r in rows})
        self.assertTrue(any(r.get("sha256") == w.digest(self.secret.encode()) for r in rows))
    def test_host_claim_not_verification(self):
        j=self.call()
        self.assertEqual(j["host_self_declared"], "cursor")
        self.assertFalse(j["host_executable_identity_verified"])
        self.assertEqual(j["skill_loading"], "UNKNOWN_NOT_WITNESSED")
    def test_owner_approval_not_inferred(self):
        j=self.call()
        self.assertEqual(j["owner_approval"], "NOT_OBSERVED")
        self.assertEqual(j["release"], "HOLD")
    def test_git_absent_not_fabricated(self):
        j=self.call()
        self.assertIsNone(j["git"]["head_sha"])
        self.assertEqual(j["git"]["git_status"], "UNKNOWN")
    def test_framework_markers_not_scripts_executed(self):
        j=self.call()
        self.assertIn("node", j["framework_signals"])
        self.assertNotIn("DO NOT RUN", json.dumps(j))
    def test_selected_license_hold_maintained(self):
        j=self.call(intent="components")
        self.assertIn("DavidHDev/react-bits", {x["repo"] for x in j["project_fit"]["deferred"]})
    def test_witness_hash_deterministic(self):
        j=self.call()
        h=j.pop("witness_sha256")
        self.assertEqual(h, w.digest(w.canonical(j)))
    def test_no_absolute_path_disclosure(self):
        j=self.call()
        self.assertNotIn(str(self.root), json.dumps(j))
        self.assertFalse(j["caller_path_disclosed"])
    def test_nonexistent_project_rejected(self):
        with self.assertRaises(FileNotFoundError):
            w.capture(str(self.root/"does-not-exist"),"cursor","design")
    def test_invalid_host_rejected(self):
        with self.assertRaisesRegex(ValueError,"unrecognized"):
            w.capture(str(self.root),"fakeroot","design")
    def test_oversized_policy_hold(self):
        (self.root/"GEMINI.md").write_bytes(b"X"*(w.MAX_POLICY_BYTES+1))
        j=self.call()
        self.assertEqual(j["audit_status"],"HOLD_INCOMPLETE_OR_UNSAFE_OBSERVATION")
        self.assertNotIn("X"*200, json.dumps(j))
    def test_host_agent_dir_marked(self):
        self.assertIn("adapters:.cursor/rules", self.call()["framework_signals"])
    def test_intent_is_reference_only(self):
        self.assertEqual(self.call(intent="motion")["project_fit"]["classification"],"REFERENCE_RECOMMENDATION_ONLY")
    @unittest.skipUnless(os.name != "nt", "Windows symlink permissions not guaranteed")
    def test_symlink_policy_is_never_followed(self):
        (self.root/"GEMINI.md").symlink_to(self.root/"AGENTS.md")
        j=self.call()
        self.assertTrue(any(r["state"] == "SYMLINK_HOLD" for r in j["observed_policy_files"]))
        self.assertEqual(j["audit_status"],"HOLD_INCOMPLETE_OR_UNSAFE_OBSERVATION")

if __name__ == "__main__":unittest.main()
