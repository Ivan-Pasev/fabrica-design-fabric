"""Ω11I v0.3 fail-closed source-native reconciliation and baseline retention."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

HERE=Path(__file__).resolve().parent.parent/"db"
SPEC=importlib.util.spec_from_file_location("omega11i_reconcile",HERE/"reconcile_native_v03.py")
R=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(R)
SNAP=HERE/"native_snapshot_2026-11-14_v0.3.json"
ENV_BASE="FAB_VISUAL_V02_BASE"

class SourceSnapshot(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.data=json.loads(SNAP.read_text())
        self.snap=self.root/"reviewed.json"
        self.save()
    def save(self):
        self.snap.write_text(json.dumps(self.data))
    def load(self):
        self.save();return R.read_snapshot(self.snap)[0]
    def test_exact_source_readback_43_52(self):
        d=self.load()
        self.assertEqual(len(d["gates"]),43)
        self.assertEqual(len(d["evidence"]),52)
        self.assertEqual(d["expected_counts"],R.CURRENT_COUNTS)
        self.assertEqual(d["revision_integrity"],"READ_ONLY_MODIFIED_TIME_NOT_CAS")
        self.assertEqual(d["human_signature"],"NOT_PRESENT")
        self.assertEqual(d["release"],"HOLD")
    def test_old_fail_status_rejected(self):
        self.data["gates"][2]["status"]="PASS"
        with self.assertRaises(ValueError):self.load()
    def test_release_hold_cannot_promote(self):
        next(g for g in self.data["gates"] if g["gate_id"]=="G11.12")["status"]="PASS"
        with self.assertRaises(ValueError):self.load()
    def test_virtual_clock_observer_uncertainty_cannot_promote(self):
        next(g for g in self.data["gates"] if g["gate_id"]=="G11.38")["status"]="PASS"
        with self.assertRaises(ValueError):self.load()
    def test_real_frame_depth_cannot_admit(self):
        next(g for g in self.data["gates"] if g["gate_id"]=="G11.39")["status"]="PASS"
        with self.assertRaises(ValueError):self.load()
    def test_revision_token_forgery_refused(self):
        self.data["provider_revision_token"]="MANUFACTURED"
        with self.assertRaises(ValueError):self.load()
    def test_human_signature_forgery_refused(self):
        self.data["human_signature"]="REVIEWED"
        with self.assertRaises(ValueError):self.load()
    def test_incomplete_source_rejected(self):
        self.data["evidence"].pop()
        with self.assertRaises(ValueError):self.load()
    def test_duplicate_new_gate_rejected(self):
        self.data["gates"][42]["gate_id"]="G11.38"
        with self.assertRaises(ValueError):self.load()
    def test_duplicate_evidence_rejected(self):
        self.data["evidence"][-1]=copy.deepcopy(self.data["evidence"][-2])
        with self.assertRaises(ValueError):self.load()
    def test_sheet_identity_not_replaceable(self):
        self.data["source_sheet"]="https://attacker.invalid"
        with self.assertRaises(ValueError):self.load()
    def test_release_metadata_must_be_hold(self):
        self.data["release"]="GO_PUBLIC"
        with self.assertRaises(ValueError):self.load()
    def test_baseline_sha_anchor_refusal(self):
        self.data["baseline_db_sha256"]="0"*64
        with self.assertRaises(ValueError):self.load()
    def test_snapshot_range_mismatch_rejected(self):
        self.data["gate_range"]="Gate Registry!A7:H90"
        with self.assertRaises(ValueError):self.load()


@unittest.skipUnless(os.environ.get(ENV_BASE),"Requires exact downloaded Ω11H baseline from CI")
class ExactBaselineIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.base=Path(os.environ[ENV_BASE])
        if not self.base.is_file():
            raise ValueError("missing exact v0.2 baseline")
        self.out=self.root/"v0.3.sqlite"
        self.receipt=self.root/"receipt.json"
    def migrate(self):
        return R.reconcile(self.base,SNAP,self.out,self.receipt)
    def test_eight_historical_checkpoints_are_preserved(self):
        before=R.sha(self.base.read_bytes())
        with sqlite3.connect(self.base) as conn:
            checkpoint_ids=[row[0] for row in conn.execute("SELECT checkpoint_id FROM checkpoint_events ORDER BY rowid")]
        self.assertEqual(len(checkpoint_ids),8)
        x=self.migrate()
        self.assertEqual(x["checkpoint_ids_preserved"],8)
        self.assertEqual(x["new_gates"],6)
        self.assertEqual(x["new_evidence"],8)
        self.assertEqual(x["total_gates"],43)
        self.assertEqual(x["total_evidence"],52)
        self.assertEqual(x["provider_revision"],"NOT_AVAILABLE")
        self.assertEqual(x["human_signature"],"NOT_PRESENT")
        self.assertEqual(x["release"],"HOLD")
        self.assertEqual(R.sha(self.base.read_bytes()),before)
        self.assertEqual(R.sha(self.out.read_bytes()),x["candidate_db_sha256"])
        with sqlite3.connect(self.out) as conn:
            new_ids=[row[0] for row in conn.execute("SELECT checkpoint_id FROM checkpoint_events ORDER BY rowid")]
            self.assertEqual(new_ids,checkpoint_ids)
            self.assertEqual(dict(conn.execute("SELECT status,total FROM gate_counts")),R.CURRENT_COUNTS)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM evidence").fetchone()[0],52)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM ci_runs").fetchone()[0],3)
            self.assertEqual(conn.execute("PRAGMA foreign_key_check").fetchall(),[])
            self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    def test_baseline_is_non_mutable_and_output_cannot_overwrite(self):
        self.migrate()
        with self.assertRaises(ValueError):self.migrate()
    def test_old_history_modified_fails_closed(self):
        corrupted=self.root/"corrupted.json"
        o=json.loads(SNAP.read_text());o["gates"][0]["predicate"]="corrupted past"
        corrupted.write_text(json.dumps(o))
        with self.assertRaises(ValueError):
            R.reconcile(self.base,corrupted,self.out,self.receipt)
        self.assertFalse(self.out.exists())
    def test_modified_evidence_fails_closed(self):
        corrupted=self.root/"corrupted.json"
        o=json.loads(SNAP.read_text());o["evidence"][4]["title"]="rewritten history"
        corrupted.write_text(json.dumps(o))
        with self.assertRaises(ValueError):
            R.reconcile(self.base,corrupted,self.out,self.receipt)
        self.assertFalse(self.out.exists())
    def test_tampered_baseline_byte_rejected(self):
        fake=self.root/"tampered.sqlite";shutil.copyfile(self.base,fake)
        with fake.open("ab") as f:f.write(b"tampered")
        with self.assertRaises(ValueError):
            R.reconcile(fake,SNAP,self.out,self.receipt)
        self.assertFalse(self.out.exists())
    def test_reconciliation_output_never_writes_input_path(self):
        with self.assertRaises(ValueError):
            R.reconcile(self.base,SNAP,self.base,self.receipt)

if __name__=="__main__":unittest.main()
