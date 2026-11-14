"""Adversarial constitutional SQLite build/append-only/reproducibility tests."""
import copy
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

PATH=Path(__file__).resolve().parent.parent/"db"
SPEC=importlib.util.spec_from_file_location("fab_visual_central_db",PATH/"build_registry.py")
DB=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DB)


class ConstitutionalEvidenceDb(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home=Path(self.temp.name)
        self.source=PATH/"canonical_seed_2026-11-14.json"
        self.seed=json.loads(self.source.read_text())
        self.out=self.home/"FAB_VISUAL.db"
        self.receipt=self.home/"snapshot-receipt.json"

    def build(self):
        return DB.build(self.source,PATH/"schema.sql",self.out,self.receipt)

    def write_seed(self,obj):
        p=self.home/"mutated.json"
        p.write_text(json.dumps(obj))
        return p

    def test_registry_snapshot_build_and_counts(self):
        r=self.build()
        self.assertEqual(r["status_counts"],{"PASS":16,"FAIL":6,"NOT_RUN":9,"HOLD":1})
        self.assertEqual(r["frame_attestation"],"NOT_ADMITTED")
        self.assertEqual(r["real_mesh_depth"],"NOT_RUN")
        with sqlite3.connect(self.out) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM gate_current").fetchone()[0],32)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM evidence").fetchone()[0],35)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM checkpoint_events").fetchone()[0],0)
            self.assertEqual(conn.execute("SELECT value FROM metadata WHERE key='release'").fetchone()[0],"HOLD")
            self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual(conn.execute("PRAGMA foreign_key_check").fetchall(),[])

    def test_database_file_is_reproducible_for_exact_seed(self):
        first=self.build()["database_sha256"]
        self.out.unlink()
        self.receipt.unlink()
        again=self.build()["database_sha256"]
        self.assertEqual(first,again)

    def test_rebuild_never_overwrites_existing(self):
        self.build()
        with self.assertRaises(ValueError):
            self.build()

    def test_original_source_pin_forgery_rejected(self):
        wrong=copy.deepcopy(self.seed)
        wrong["original_upstream"]["commit"]="e"*40
        with self.assertRaises(ValueError):
            DB.read_seed(self.write_seed(wrong))

    def test_unexpected_source_sheet_rejected(self):
        wrong=copy.deepcopy(self.seed)
        wrong["gate_sheet_source"]["url"]="https://attacker.invalid/sheet"
        with self.assertRaises(ValueError):
            DB.read_seed(self.write_seed(wrong))

    def test_authority_inversion_rejected(self):
        wrong=copy.deepcopy(self.seed)
        wrong["canonical_authority"]="DATABASE_OVERRIDES_NATIVE"
        with self.assertRaises(ValueError):
            DB.read_seed(self.write_seed(wrong))

    def test_automatic_bidirectional_sync_rejected(self):
        wrong=copy.deepcopy(self.seed)
        wrong["no_automatic_bidirectional_sync"]=False
        with self.assertRaises(ValueError):
            DB.read_seed(self.write_seed(wrong))

    def test_release_gate_must_remain_hold(self):
        wrong=copy.deepcopy(self.seed)
        target=next(x for x in wrong["gates"] if x["gate_id"]=="G11.12")
        target["status"]="PASS"
        with self.assertRaises(ValueError):
            DB.read_seed(self.write_seed(wrong))

    def test_duplicate_gate_id_rejected(self):
        wrong=copy.deepcopy(self.seed)
        wrong["gates"][2]["gate_id"]=wrong["gates"][1]["gate_id"]
        with self.assertRaises(ValueError):
            DB.read_seed(self.write_seed(wrong))

    def test_missing_evidence_rejected(self):
        wrong=copy.deepcopy(self.seed)
        wrong["evidence"].pop()
        with self.assertRaises(ValueError):
            DB.read_seed(self.write_seed(wrong))

    def test_gate_status_events_are_append_only(self):
        self.build()
        with sqlite3.connect(self.out) as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("UPDATE gate_events SET status='PASS' WHERE gate_id='G10.3'")
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("DELETE FROM gate_events WHERE gate_id='G10.3'")

    def test_evidence_rows_are_append_only(self):
        self.build()
        with sqlite3.connect(self.out) as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("UPDATE evidence SET result='PASS'")
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("DELETE FROM evidence")

    def test_checkpoint_records_can_never_admit_real_frame(self):
        self.build()
        with sqlite3.connect(self.out) as conn:
            columns=("checkpoint_id","scene","source_head","source_html_sha256",
                     "derivative_sha256","mode","applied_update_ordinal",
                     "source_state_sha256","frame_attestation","depth_attestation",
                     "evidence_uri","provenance_source_id")
            values=("a"*64,"raptor-light","b"*40,"a"*64,"b"*64,
                    "OBSERVING_DERIVATIVE",3,None,"FRAME_VERIFIED","NOT_RUN",
                    "https://github.com/test","research-pr31")
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(f"INSERT INTO checkpoint_events ({','.join(columns)}) VALUES ({','.join('?' for x in columns)})",values)

    def test_foreign_keys_reject_forged_provenance(self):
        self.build()
        with sqlite3.connect(self.out) as conn:
            conn.execute("PRAGMA foreign_keys=ON")
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("""INSERT INTO ci_runs
                  (run_id,source_head,original_pin,github_uri,result,grade,release,provenance_source_id)
                  VALUES (?,?,?,?,?,?,?,?)""",
                  (1,"a"*40,DB.PIN,"https://github.com/test",
                   "PASS","SYNTHETIC","HOLD","NO_SUCH_PROVENANCE"))

    def test_historical_fail_and_release_hold_remain(self):
        self.build()
        with sqlite3.connect(self.out) as conn:
            got={k:v for k,v in conn.execute("SELECT gate_id,status FROM gate_current")}
            for id in ("G10.3","G11.14","G11.18","G11.21","G11.22","G11.28"):
                self.assertEqual(got[id],"FAIL")
            self.assertEqual(got["G11.12"],"HOLD")

    def test_snapshots_do_not_invent_runtime_frame_evidence(self):
        self.build()
        with sqlite3.connect(self.out) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM checkpoint_events").fetchone()[0],0)
            sources={x[0]:x[1] for x in conn.execute("SELECT source_id,authority FROM sources")}
            self.assertEqual(sources["native-gate-sheet"],"SHEET_AUTHORITATIVE")
            self.assertEqual(sources["original-anatomy"],"ORIGINAL_IMMUTABLE")


if __name__=="__main__":unittest.main()
