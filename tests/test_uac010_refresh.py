"""UAC-010 sourced refresh ledger: never rewrite historical pins from observed HEADs."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
def get(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))

class SelectedRefreshTests(unittest.TestCase):
    def test_three_selected_only(self):
        self.assertEqual(len(get("registry/uac010_selected_source_refresh.json")["selected"]),3)
    def test_historical_pins_not_changed(self):
        registry={r["repo"]:r for r in get("registry/third_party_sources.v1.json")["repositories"]}
        for r in get("registry/uac010_selected_source_refresh.json")["selected"]:
            self.assertEqual(r["historical_pin"], registry[r["repo"]]["source_commit"])
    def test_license_files_recorded_not_global_approval(self):
        d=get("registry/uac010_selected_source_refresh.json")
        self.assertTrue(all(r["license_file"]=="LICENSE" and len(r["license_git_blob"])==40 for r in d["selected"]))
        self.assertFalse(d["immutable_policy"]["human_review_verified"])
        self.assertFalse(d["immutable_policy"]["host_install_verified"])
    def test_upstream_drifts_not_promoted(self):
        d=get("registry/uac010_selected_source_refresh.json")
        self.assertEqual(sorted(x["ahead_from_recorded_pin"] for x in d["selected"]),[0,28,76])
        self.assertFalse(d["immutable_policy"]["auto_upgrade"])
    def test_repo_specific_current_pin(self):
        d=get("registry/uac010_selected_source_refresh.json")
        ek=next(x for x in d["selected"] if x["repo"]=="emilkowalski/skills")
        self.assertEqual(ek["historical_pin"], ek["observed_head"])
if __name__=="__main__":unittest.main()
