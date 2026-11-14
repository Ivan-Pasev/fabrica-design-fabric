"""Ω11H: reviewed source-snapshot reconciliation with no historical rewrites."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

HERE=Path(__file__).resolve().parent.parent/"db"
def load(filename):
    s=importlib.util.spec_from_file_location(filename.replace(".","_"),HERE/filename)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
D=load("build_registry.py")
R=load("reconcile_native_v02.py")

class NativeReconciliation(unittest.TestCase):
    def setUp(self):
        x=tempfile.TemporaryDirectory();self.addCleanup(x.cleanup)
        self.root=Path(x.name)
        self.baseline=self.root/"baseline.sqlite"
        self.initial=self.root/"initial.json"
        D.build(HERE/"canonical_seed_2026-11-14.json",HERE/"schema.sql",self.baseline,self.initial)
        self.snap=json.loads((HERE/"native_snapshot_2026-11-14_v0.2.json").read_text())
        self.snapshot=self.root/"source.json";self.save()
        self.output=self.root/"candidate.sqlite"
        self.receipt=self.root/"receipt.json"
    def save(self): self.snapshot.write_text(json.dumps(self.snap))
    def migrate(self):
        self.save()
        return R.reconcile(self.baseline,self.snapshot,self.output,self.receipt)

    def test_native_sheet_is_still_authority(self):
        r=self.migrate()
        self.assertEqual(r["total_gates"],37)
        self.assertEqual(r["total_evidence"],44)
        self.assertEqual(r["checkpoint_ids_preserved"],0)
        self.assertEqual(r["authority"],"NATIVE_SHEET_AUTHORITATIVE")
        self.assertEqual(r["human_signature"],"NOT_PRESENT")
        self.assertEqual(r["admission"],"RESEARCH_SNAPSHOT_ONLY")
        self.assertEqual(r["gate_counts"],{"PASS":19,"FAIL":6,"NOT_RUN":10,"HOLD":1,"INCONCLUSIVE":1})
        with sqlite3.connect(self.output) as db:
            self.assertEqual(dict(db.execute("SELECT status,total FROM gate_counts")),R.CURRENT_COUNTS)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM gate_events").fetchone()[0],37)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM evidence").fetchone()[0],44)
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
            self.assertEqual(dict(db.execute("SELECT gate_id,status FROM gate_current"))["G11.32"],"INCONCLUSIVE")
            self.assertEqual(dict(db.execute("SELECT gate_id,status FROM gate_current"))["G11.33"],"NOT_RUN")

    def test_baseline_immutable(self):
        sha=D.digest(self.baseline.read_bytes())
        self.migrate()
        self.assertEqual(D.digest(self.baseline.read_bytes()),sha)

    def test_overwrite_refusal(self):
        self.migrate()
        with self.assertRaises(ValueError):self.migrate()

    def test_existing_gate_mutation_rejected(self):
        self.snap["gates"][0]["predicate"]="mismatched old theorem"
        with self.assertRaises(ValueError):self.migrate()

    def test_existing_evidence_mutation_rejected(self):
        self.snap["evidence"][0]["result"]="PASS_ALL"
        with self.assertRaises(ValueError):self.migrate()

    def test_old_fail_gate_promotion_rejected(self):
        g=next(g for g in self.snap["gates"] if g["gate_id"]=="G10.3")
        g["status"]="PASS"
        with self.assertRaises(ValueError):self.migrate()

    def test_release_hold_promotion_rejected(self):
        g=next(g for g in self.snap["gates"] if g["gate_id"]=="G11.12")
        g["status"]="PASS"
        with self.assertRaises(ValueError):self.migrate()

    def test_inconclusive_promoted_to_pass_rejected(self):
        g=next(g for g in self.snap["gates"] if g["gate_id"]=="G11.32")
        g["status"]="PASS"
        with self.assertRaises(ValueError):self.migrate()

    def test_bad_source_sheet_rejected(self):
        self.snap["source_sheet"]="https://attacker.invalid"
        with self.assertRaises(ValueError):self.migrate()

    def test_provider_revision_claim_without_receipt_rejected(self):
        self.snap["provider_revision_token"]="FAKE_VERIFIED"
        with self.assertRaises(ValueError):self.migrate()

    def test_forged_human_signature_rejected(self):
        self.snap["human_signature"]="yes"
        with self.assertRaises(ValueError):self.migrate()

    def test_invalid_base_sha_rejected(self):
        with self.baseline.open("ab") as f:f.write(b"tamper")
        with self.assertRaises(ValueError):self.migrate()

    def test_duplicate_new_gate_id_rejected(self):
        self.snap["gates"][36]["gate_id"]="G11.32"
        with self.assertRaises(ValueError):self.migrate()

    def test_duplicate_evidence_record_rejected(self):
        self.snap["evidence"][43]=copy.deepcopy(self.snap["evidence"][42])
        with self.assertRaises(ValueError):self.migrate()

    def test_output_fails_closed_when_source_drift_detected(self):
        self.snap["evidence"][11]["title"]="tampered historical record"
        with self.assertRaises(ValueError):self.migrate()
        self.assertFalse(self.output.exists())
        self.assertFalse(self.receipt.exists())

if __name__=="__main__":unittest.main()
