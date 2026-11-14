"""Ω11G evidence ingestion contracts: source-bound 12-process proof -> 8 DB rows."""
from __future__ import annotations
import copy
import importlib.util
import json
import hashlib
from pathlib import Path
import sqlite3
import tempfile
import unittest

DBROOT=Path(__file__).resolve().parent.parent/"db"

def load(name):
    spec=importlib.util.spec_from_file_location(name.replace("-","_"),DBROOT/name)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

D=load("build_registry.py")
I=load("ingest_checkpoints.py")
H="a"*40
ORIG={
 "raptor-light":"48f64b954b93567f1a5ca87fa823c34ae9e81842fa5b95512deba6b22b37a537",
 "turning-light":"e175e82f1bba087bb6031e375fb5da386f4f779e89e91a7864f7fc298b8b14e3"
}
SCENES=("raptor-light","turning-light")
MODES=("minimal","observing")
RUN=44444000


def manifest():
    values={}
    for scene in SCENES:
        for side in MODES:
            mode="MINIMAL_CHECKPOINT" if side=="minimal" else "OBSERVING_CHECKPOINT"
            values[scene+"|"+mode]={
              "scene":scene,"mode":mode,
              "source_commit":D.PIN,
              "original_html_sha256":ORIG[scene],
              "derivative_html_sha256":D.digest((scene+"|"+side).encode())
            }
    return {"source_commit":D.PIN,"checkpoint_target":3,
            "frame_attestation":"NOT_ADMITTED","real_depth":"NOT_RUN",
            "release":"HOLD","variants":values}


def receipt(m):
    observations=[]
    for scene in SCENES:
        for side in ("original","minimal","observing"):
            for proc in (0,1):
                grade=("AFTER_RAPTOR_TICK_DOM_UPDATE_BEFORE_PRESENT"
                       if scene=="raptor-light"
                       else "AFTER_TURNING_CONTROLLER_SET_BEFORE_PRESENT")
                events=[]
                if side=="observing":
                    state=({"burn":{},"springs":{}}
                           if scene=="raptor-light"
                           else {"applied_controller_state":{"table":0.1,"lift":1,"time":0.01}})
                    events=[{"serial":j,"renderer_present_barrier":"NOT_AVAILABLE",
                             "applied_state":copy.deepcopy(state)} for j in (1,2,3)]
                chk=None if side=="original" else {
                  "schema":"fab.visual.omega11g.control.v1","scene":scene,
                  "mode":"MINIMAL_CHECKPOINT" if side=="minimal" else "OBSERVING_CHECKPOINT",
                  "applied_state_grade":grade,
                  "target":3,"serial":3,"done":True,
                  "actual_renderer_frame":"NOT_ADMITTED","actual_mesh_depth":"NOT_RUN",
                  "events":events
                }
                key=scene+"|"+("MINIMAL_CHECKPOINT" if side=="minimal" else "OBSERVING_CHECKPOINT")
                h=ORIG[scene] if side=="original" else m["variants"][key]["derivative_html_sha256"]
                observations.append({
                  "scene":scene,"side":side,"process":proc,
                  "html_sha256":h,"checkpoint":chk,
                  "source_defined_stage":{"selector":".rp-stage" if scene=="raptor-light" else ".ts-stage",
                                          "rect":[0,0,350,250]},
                  "classification":"PASS_ORIGINAL_UNINSTRUMENTED" if side=="original" else "PASS_FIXED_APPLICATION_ORDINAL_ONLY",
                  "errors":[],"blocked_external_requests":[]
                })
    return {
     "source_commit":D.PIN,"checkpoint_ordinal":3,"fixed_applied_update_gate":"PASS_DERIVATIVE_ORDINAL_ONLY",
     "renderer_presented_frame":"NOT_ADMITTED","real_anatomy_geometry_depth":"NOT_RUN",
     "applied_state_equivalence":"INCONCLUSIVE_UNCONTROLLED_RAF_TIME",
     "release":"HOLD","observations":observations
    }


class IngestProofBoundary(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.db=self.root/"fab.sqlite"
        D.build(DBROOT/"canonical_seed_2026-11-14.json",DBROOT/"schema.sql",
                self.db,self.root/"initial.json")
        self.man=manifest()
        self.browser=receipt(self.man)
        self.man_file=self.root/"manifest.json"
        self.browser_file=self.root/"browser.json"
        self.head_file=self.root/"HEAD.txt"
        self.final_file=self.root/"final.json"
        self.head_file.write_text(H+"\n")
        self.save()

    def save(self):
        self.man_file.write_text(json.dumps(self.man))
        self.browser_file.write_text(json.dumps(self.browser))

    def ingest(self):
        self.save()
        return I.ingest(self.db,self.man_file,self.browser_file,
                        self.head_file,RUN,self.final_file)

    def test_eight_source_bound_checkpoints_inserted(self):
        out=self.ingest()
        self.assertEqual(out["number_derivative_checkpoint_rows"],8)
        self.assertEqual(out["number_original_uninstrumented"],4)
        self.assertEqual(out["observer_state_snapshot_rows"],4)
        self.assertEqual(out["real_presented_frame"],"NOT_ADMITTED")
        self.assertEqual(out["release"],"HOLD")
        self.assertEqual(out["final_db_sha256"],D.digest(self.db.read_bytes()))
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute("SELECT count(*) FROM checkpoint_events").fetchone()[0],8)
            self.assertEqual(c.execute("SELECT count(*) FROM checkpoint_events WHERE source_state_sha256 IS NOT NULL").fetchone()[0],4)
            self.assertEqual(c.execute("SELECT count(*) FROM ci_runs").fetchone()[0],3)
            self.assertEqual(dict(c.execute("SELECT status,total FROM gate_counts")),D.EXPECTED)
            self.assertEqual(c.execute("PRAGMA foreign_key_check").fetchall(),[])

    def test_cannot_reingest_to_existing_db(self):
        self.ingest()
        with self.assertRaises(ValueError):
            self.ingest()

    def test_forged_scene_source_html_rejected(self):
        self.man["variants"]["raptor-light|OBSERVING_CHECKPOINT"]["original_html_sha256"]="e"*64
        with self.assertRaises(ValueError):
            self.ingest()

    def test_forged_original_page_source_rejected(self):
        self.browser["observations"][0]["html_sha256"]="e"*64
        with self.assertRaises(ValueError):
            self.ingest()

    def test_duplicate_process_identity_rejected(self):
        self.browser["observations"][1]["process"]=0
        with self.assertRaises(ValueError):
            self.ingest()

    def test_missing_original_not_admitted(self):
        self.browser["observations"].pop(0)
        with self.assertRaises(ValueError):
            self.ingest()

    def test_forged_renderer_frame_rejected(self):
        self.browser["observations"][4]["checkpoint"]["actual_renderer_frame"]="FRAME_VERIFIED"
        with self.assertRaises(ValueError):
            self.ingest()

    def test_stale_checkpoint_event_rejected(self):
        self.browser["observations"][4]["checkpoint"]["serial"]=2
        with self.assertRaises(ValueError):
            self.ingest()

    def test_fake_checkpoint_mode_rejected(self):
        self.browser["observations"][4]["checkpoint"]["mode"]="OBSERVING_CHECKPOINT"
        with self.assertRaises(ValueError):
            self.ingest()

    def test_wrong_stage_rejected(self):
        self.browser["observations"][4]["source_defined_stage"]["selector"]=".iso-plate svg"
        with self.assertRaises(ValueError):
            self.ingest()

    def test_observer_applied_state_missing_rejected(self):
        self.browser["observations"][10]["checkpoint"]["events"][2]["applied_state"]={}
        with self.assertRaises(ValueError):
            self.ingest()

    def test_controller_time_equivalence_claim_rejected(self):
        self.browser["applied_state_equivalence"]="VERIFIED"
        with self.assertRaises(ValueError):
            self.ingest()

    def test_missing_evidence_readout_rejected(self):
        self.browser["observations"][5]["checkpoint"]["events"]=[]
        with self.assertRaises(ValueError):
            self.ingest()

    def test_forged_release_rejected(self):
        self.man["release"]="GO_PUBLIC"
        with self.assertRaises(ValueError):
            self.ingest()


if __name__=="__main__":unittest.main()
