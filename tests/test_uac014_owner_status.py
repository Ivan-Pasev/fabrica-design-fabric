"""UAC-014: privacy-minimized owner pilot status; source-only checks, not IDE evidence."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC=importlib.util.spec_from_file_location("fdf_owner_status",ROOT/"tools"/"fdf_owner_status.py")
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class OwnerStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.private="DO_NOT_PUBLISH_PROJECT_LAW"
        (self.root/"AGENTS.md").write_text(self.private,encoding="utf-8")

    def fake(self):
        return {
            "schema":"fdf.projectdna.local_witness/0.1",
            "project_name":"PRIVATE_OWNER_PROJECT",
            "host_self_declared":"antigravity",
            "framework_signals":["node","adapters:.cursor/rules","custom-secret-platform"],
            "observed_policy_files":[{"relative_path":"AGENTS.md","state":"PRESENT_HASH_ONLY",
                                      "sha256":"a"*64,"bytes":99}],
            "policy_inventory_truncated":False,
            "unsafe_adapter_paths":[],
            "audit_status":"LOCAL_METADATA_ONLY",
            "git":{"git_status":"CLEAN","head_sha":"b"*40},
            "project_fit":{"recommended_references":[{"repo":"internal-private-repo"}]},
        }

    def test_no_project_name_policy_paths_or_digests_leak(self):
        report=json.dumps(mod.summarize(self.fake(),mod.inspect_on_disk_candidates(self.root)))
        for forbidden in ("PRIVATE_OWNER_PROJECT","AGENTS.md","a"*64,"b"*40,"internal-private-repo"):
            self.assertNotIn(forbidden,report)
        self.assertIn("PRESENT_HASH_ONLY",report)

    def test_host_not_authenticated(self):
        data=mod.summarize(self.fake(),mod.inspect_on_disk_candidates(self.root))
        self.assertTrue(data["declared_host_not_authenticated"])
        self.assertEqual(data["release"],"HOLD")
        self.assertFalse(data["permissions_to_install_or_modify"])

    def test_framework_signals_allowlisted(self):
        data=mod.summarize(self.fake(),mod.inspect_on_disk_candidates(self.root))
        self.assertEqual(data["framework_marker_types"],["node"])

    def test_unrecognized_git_state_not_repeated(self):
        fake=self.fake()
        fake["git"]["git_status"]="PRIVATE_GIT_DETAIL"
        self.assertEqual(mod.summarize(fake,mod.inspect_on_disk_candidates(self.root))["git_state"],"UNKNOWN")

    def test_skill_file_present_is_not_activation(self):
        skill=self.root/".agents"/"skills"/"fdf-project-observer"
        skill.mkdir(parents=True)
        (skill/"SKILL.md").write_text("Lower-trust local file, not host activation",encoding="utf-8")
        data=mod.inspect_on_disk_candidates(self.root)
        self.assertIn("fdf-project-observer",data["fdf_skill_file_candidates_on_disk"])
        self.assertFalse(data["native_host_skill_discovery_verified"])
        self.assertFalse(data["native_host_skill_activation_verified"])
        self.assertFalse(data["source_identity_of_local_skill_files_verified"])

    def test_arbitrary_skill_name_not_exposed(self):
        p=self.root/".gemini"/"skills"/"private-internal-skill"
        p.mkdir(parents=True)
        (p/"SKILL.md").write_text("private",encoding="utf-8")
        data=mod.inspect_on_disk_candidates(self.root)
        self.assertEqual(data["fdf_skill_file_candidates_on_disk"],[])

    def test_nonevidence_report_keeps_status_hold(self):
        data=mod.summarize(self.fake(),mod.inspect_on_disk_candidates(self.root))
        self.assertEqual(data["classification"],"LOCAL_METADATA_OBSERVATION_NOT_IDE_ACTIVATION")
        self.assertFalse(data["independent_human_witness_present"])
        self.assertEqual(data["global_and_effective_host_rules"],"UNKNOWN_NOT_INSPECTED")

    def test_malformed_policy_inventory_fails_closed(self):
        fake=self.fake()
        fake["observed_policy_files"]=[{"state":["malformed"]}]
        with self.assertRaisesRegex(ValueError,"malformed ProjectDNA"):
            mod.summarize(fake,mod.inspect_on_disk_candidates(self.root))

    def test_actual_fixture_no_project_file_modification(self):
        before={p.relative_to(self.root).as_posix():p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}
        report=mod.status(str(self.root),"antigravity","design")
        after={p.relative_to(self.root).as_posix():p.read_bytes()
               for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before,after)
        output=json.dumps(report)
        self.assertNotIn(str(self.root),output)
        self.assertNotIn(self.private,output)
        self.assertFalse(report["permissions_to_install_or_modify"])

    def test_nonexistent_project_fails(self):
        with self.assertRaises(FileNotFoundError):
            mod.status(str(self.root/"does-not-exist"),"cursor","design")

    def test_invalid_host_fails(self):
        with self.assertRaisesRegex(ValueError,"unrecognized"):
            mod.status(str(self.root),"unverified-host","design")

    def test_policy_truncation_sets_hold(self):
        fake=self.fake()
        fake["policy_inventory_truncated"]=True
        self.assertEqual(
            mod.summarize(fake,mod.inspect_on_disk_candidates(self.root))["status"],
            "HOLD_UNSAFE_OR_INCOMPLETE_FILESYSTEM_INVENTORY")

    def test_unsupported_path_does_not_trigger_install(self):
        data=mod.inspect_on_disk_candidates(self.root)
        self.assertTrue(data["source_file_presence_is_not_host_activation"])
        self.assertNotIn("permission_to_install",data)

    @unittest.skipIf(os.name=="nt","Windows symlink privileges are not guaranteed")
    def test_symlinked_skill_directory_marks_unsafe(self):
        target=self.root/"private"
        target.mkdir()
        (self.root/".agents").symlink_to(target,target_is_directory=True)
        data=mod.inspect_on_disk_candidates(self.root)
        self.assertTrue(data["unsafe_skill_paths_detected"])
        self.assertEqual(data["fdf_skill_file_candidates_on_disk"],[])


if __name__=="__main__":
    unittest.main()



class PrivateErrorOutputTests(unittest.TestCase):
    def test_missing_workspace_error_does_not_echo_path(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as t:
            secret = str(Path(t) / "CONFIDENTIAL_OWNER_WORKSPACE_NAME")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                status = mod.main(["status","--project",secret,"--host","antigravity","--intent","design"])
            self.assertEqual(status,2)
            self.assertIn("HOLD: CALLER_WORKSPACE_NOT_ACCESSIBLE",err.getvalue())
            self.assertNotIn(secret,err.getvalue())
            self.assertNotIn("CONFIDENTIAL_OWNER_WORKSPACE_NAME",err.getvalue())



class MetadataOnlyReadBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "AGENTS.md").write_text("CONFIDENTIAL_POLICY_DATA", encoding="utf-8")

    def test_no_policy_content_reads_git_or_legacy_capture(self):
        import subprocess
        with patch.object(Path, "read_bytes", side_effect=AssertionError("policy bytes read")), \
             patch.object(subprocess, "run", side_effect=AssertionError("Git subprocess invoked")), \
             patch.object(mod.fdf_projectdna, "capture",
                          side_effect=AssertionError("legacy hash witness invoked")):
            result = mod.status(str(self.root), "antigravity", "design")
        self.assertFalse(result["policy_file_contents_accessed"])
        self.assertFalse(result["policy_file_hashes_computed"])
        self.assertFalse(result["git_subprocess_invoked"])
        self.assertEqual(result["git_state"], "UNKNOWN")

    def test_policy_count_is_metadata_only(self):
        result = mod.status(str(self.root), "codex", "design")
        self.assertEqual(result["bounded_policy_file_count"], 1)
        self.assertEqual(result["bounded_policy_state_counts"],
                         {"PRESENT_METADATA_ONLY": 1})
        self.assertTrue(result["policy_paths_content_and_hashes_disclosed"] is False)

    def test_hidden_git_tree_is_not_inventoried(self):
        hidden = self.root / ".git"
        hidden.mkdir()
        (hidden / "AGENTS.md").write_text("HIDDEN_CONTENT", encoding="utf-8")
        result = mod.status(str(self.root), "antigravity", "design")
        self.assertEqual(result["bounded_policy_file_count"], 1)

    def test_many_policy_files_trigger_bounded_inventory_hold(self):
        for index in range(mod.MAX_POLICY_ITEMS + 1):
            item = self.root / ("policy_" + str(index))
            item.mkdir()
            (item / "GEMINI.md").write_text("policy metadata only", encoding="utf-8")
        result = mod.status(str(self.root), "gemini-cli", "design")
        self.assertEqual(result["status"],
                         "HOLD_UNSAFE_OR_INCOMPLETE_FILESYSTEM_INVENTORY")
        self.assertLessEqual(result["bounded_policy_file_count"], mod.MAX_POLICY_ITEMS)

    def test_git_marker_is_not_committed_state_evidence(self):
        (self.root / ".git").mkdir()
        result = mod.status(str(self.root), "unknown", "design")
        self.assertEqual(result["git_state"], "UNKNOWN")
        self.assertFalse(result["native_host_skill_activation_verified"]
                         if "native_host_skill_activation_verified" in result
                         else result["on_disk"]["native_host_skill_activation_verified"])

    def test_explicit_unknown_host_will_not_authenticate(self):
        result = mod.status(str(self.root), "unknown", "design")
        self.assertTrue(result["declared_host_not_authenticated"])
        self.assertFalse(result["independent_human_witness_present"])
        self.assertEqual(result["release"], "HOLD")

    @unittest.skipIf(os.name == "nt", "Windows symlink permission varies")
    def test_symlinked_root_policy_marks_hold(self):
        (self.root / "GEMINI.md").symlink_to(self.root / "AGENTS.md")
        result = mod.status(str(self.root), "gemini-cli", "design")
        self.assertEqual(result["status"], "HOLD_UNSAFE_OR_INCOMPLETE_FILESYSTEM_INVENTORY")
        self.assertFalse(result["permissions_to_install_or_modify"])
