#!/usr/bin/env python3
"""Ω11G: append actual *instrumented derivative* checkpoint evidence to SQLite.

Uses only the exact-head CI's own provenance manifest and 12-process browser
receipt. No source status changes and NO presented-renderer frame admission.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3

HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("fab_visual_central_db",HERE/"build_registry.py")
DB=importlib.util.module_from_spec(sp);sp.loader.exec_module(DB)

def read(path):
    return json.loads(Path(path).read_text())


def ingest(database,manifest_path,browser_path,head_path,run_id,receipt_path):
    database=Path(database)
    manifest_path=Path(manifest_path)
    browser_path=Path(browser_path)
    receipt_path=Path(receipt_path)
    if receipt_path.exists():
        raise ValueError("cannot overwrite an existing checkpoint receipt")
    manifest=read(manifest_path)
    browser=read(browser_path)
    head=Path(head_path).read_text().strip()
    if len(head)!=40 or any(x not in "0123456789abcdef" for x in head):
        raise ValueError("invalid actual git review head")
    if type(run_id)!=int or run_id<=0:
        raise ValueError("GitHub CI run ID is required")
    original_sha={"raptor-light":"48f64b954b93567f1a5ca87fa823c34ae9e81842fa5b95512deba6b22b37a537",
                  "turning-light":"e175e82f1bba087bb6031e375fb5da386f4f779e89e91a7864f7fc298b8b14e3"}
    stage_selectors={"raptor-light":".rp-stage","turning-light":".ts-stage"}
    if manifest.get("source_commit")!=DB.PIN or browser.get("source_commit")!=DB.PIN:
        raise ValueError("source-pinned lineage mismatch")
    if manifest.get("frame_attestation")!="NOT_ADMITTED" or manifest.get("real_depth")!="NOT_RUN":
        raise ValueError("incorrect derivative frame/depth evidence grade")
    if manifest.get("release")!="HOLD" or browser.get("release")!="HOLD":
        raise ValueError("release cannot be admitted")
    if browser.get("fixed_applied_update_gate")!="PASS_DERIVATIVE_ORDINAL_ONLY":
        raise ValueError("the browser did not prove fixed applied ordinal")
    if browser.get("renderer_presented_frame")!="NOT_ADMITTED":
        raise ValueError("a synthetic checkpoint is not a GPU present")
    if browser.get("real_anatomy_geometry_depth")!="NOT_RUN":
        raise ValueError("real 3D mesh depth was never checked")
    if browser.get("applied_state_equivalence")!="INCONCLUSIVE_UNCONTROLLED_RAF_TIME":
        raise ValueError("cannot infer equivalent elapsed time")
    if browser.get("checkpoint_ordinal")!=3 or manifest.get("checkpoint_target")!=3:
        raise ValueError("exact target must be third actual application update")
    observations=browser.get("observations")
    if not isinstance(observations,list) or len(observations)!=12:
        raise ValueError("expected twelve independent fresh-browser observations")
    if len(manifest.get("variants",{}))!=4:
        raise ValueError("missing source-identified minimal/observing variants")
    used=set()
    rows=[]
    originals=0
    for x in observations:
        scene=x.get("scene");side=x.get("side");proc=x.get("process")
        key=(scene,side,proc)
        if key in used or scene not in ("raptor-light","turning-light") or side not in ("original","minimal","observing") or type(proc)!=int or proc not in (0,1):
            raise ValueError("duplicate or malformed source/variant/process identity")
        used.add(key)
        stage=x.get("source_defined_stage") or {}
        if stage.get("selector")!=stage_selectors[scene] or not isinstance(stage.get("rect"),list) or len(stage["rect"])!=4 or stage["rect"][2]<=20 or stage["rect"][3]<=20:
            raise ValueError("not a source-defined full-size stage")
        if x.get("errors") or x.get("blocked_external_requests"):
            raise ValueError("JavaScript error or blocked remote source in evidence")
        if side=="original":
            originals+=1
            if x.get("html_sha256")!=original_sha[scene]:
                raise ValueError("unmodified original browser HTML hash mismatch")
            if x.get("checkpoint") is not None or x.get("classification")!="PASS_ORIGINAL_UNINSTRUMENTED":
                raise ValueError("original contamination")
            continue
        if x.get("classification")!="PASS_FIXED_APPLICATION_ORDINAL_ONLY":
            raise ValueError("not an applied-state checkpoint")
        c=x.get("checkpoint")
        expected_mode="MINIMAL_CHECKPOINT" if side=="minimal" else "OBSERVING_CHECKPOINT"
        expected_grade=("AFTER_RAPTOR_TICK_DOM_UPDATE_BEFORE_PRESENT" if scene=="raptor-light"
                        else "AFTER_TURNING_CONTROLLER_SET_BEFORE_PRESENT")
        if not isinstance(c,dict) or c.get("schema")!="fab.visual.omega11g.control.v1" or c.get("scene")!=scene or c.get("mode")!=expected_mode or c.get("applied_state_grade")!=expected_grade:
            raise ValueError("invalid derived checkpoint mode, grade or scene")
        if c.get("serial")!=3 or c.get("done") is not True or c.get("target")!=3:
            raise ValueError("stale or fabricated checkpoint")
        if c.get("actual_renderer_frame")!="NOT_ADMITTED" or c.get("actual_mesh_depth")!="NOT_RUN":
            raise ValueError("forged frame/depth result")
        mode="MINIMAL_CHECKPOINT" if side=="minimal" else "OBSERVING_CHECKPOINT"
        entry=manifest["variants"].get(scene+"|"+mode)
        if not entry or entry.get("original_html_sha256")!=original_sha[scene] or entry.get("derivative_html_sha256")!=x.get("html_sha256"):
            raise ValueError("source/derivative SHA not tied to the pinned original manifest")
        if entry.get("source_commit")!=DB.PIN:
            raise ValueError("derivative source commit mismatch")
        if side=="minimal":
            if c.get("events")!=[]:
                raise ValueError("minimal control is not a no-state observation")
            state_sha=None
        else:
            events=c.get("events")
            if not isinstance(events,list) or [z.get("serial") for z in events]!=[1,2,3]:
                raise ValueError("observer event sequence does not match actual checkpoint")
            if any(z.get("renderer_present_barrier")!="NOT_AVAILABLE" for z in events):
                raise ValueError("unattested present barrier")
            snapshot=events[-1].get("applied_state")
            if not isinstance(snapshot,dict):
                raise ValueError("missing real instrumented application data")
            state_sha=DB.digest(DB.canonical(snapshot))
        payload={"ci_run_id":run_id,"git_head":head,"scene":scene,"variant":side,
                 "process":proc,"applied_ordinal":3,"source_html_sha":entry["original_html_sha256"],
                 "derivative_html_sha":entry["derivative_html_sha256"],"state_sha":state_sha}
        checkpoint_id=DB.digest(DB.canonical(payload))
        rows.append((checkpoint_id,scene,head,entry["original_html_sha256"],
                     entry["derivative_html_sha256"],
                     "MINIMAL_DERIVATIVE" if side=="minimal" else "OBSERVING_DERIVATIVE",
                     3,state_sha,"NOT_ADMITTED","NOT_RUN",
                     f"https://github.com/Ivan-Pasev/fabrica-design-fabric/actions/runs/{run_id}",
                     "omega11g-ci-"+str(run_id)))
    if originals!=4 or len(rows)!=8 or len(used)!=12:
        raise ValueError("failed exact original vs derivative process coverage")
    if not database.is_file():
        raise ValueError("missing preflight SQLite DB snapshot")
    before_sha=DB.digest(database.read_bytes())
    source_id="omega11g-ci-"+str(run_id)
    with sqlite3.connect(database) as con:
        con.execute("PRAGMA foreign_keys=ON")
        if con.execute("SELECT count(*) FROM checkpoint_events").fetchone()[0]!=0:
            raise ValueError("v0.1 DB already contains checkpoints, cannot reingest")
        if con.execute("SELECT value FROM metadata WHERE key='release'").fetchone()[0]!="HOLD":
            raise ValueError("existing DB release boundary invalid")
        con.execute("BEGIN IMMEDIATE")
        con.execute("""INSERT INTO sources(
          source_id,kind,uri,pinned_revision,sha256,authority
          ) VALUES (?,?,?,?,?,?)""",
          (source_id,"DERIVED_RECORD",
           f"https://github.com/Ivan-Pasev/fabrica-design-fabric/actions/runs/{run_id}",
           head,DB.digest(browser_path.read_bytes()),"DERIVED_ONLY"))
        con.execute("""INSERT INTO ci_runs(
          run_id,source_head,original_pin,github_uri,result,grade,release,provenance_source_id
        ) VALUES (?,?,?,?,?,?,?,?)""",
          (run_id,head,DB.PIN,
           f"https://github.com/Ivan-Pasev/fabrica-design-fabric/actions/runs/{run_id}",
           "PASS","INSTRUMENTED_DERIVATIVE","HOLD",source_id))
        con.executemany("""INSERT INTO checkpoint_events(
          checkpoint_id,scene,source_head,source_html_sha256,derivative_sha256,
          mode,applied_update_ordinal,source_state_sha256,
          frame_attestation,depth_attestation,evidence_uri,provenance_source_id
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",rows)
        con.execute("INSERT INTO metadata(key,value) VALUES (?,?)",
                    ("checkpoint_ci_run_id",str(run_id)))
        con.commit()
        if con.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("SQLite integrity check failed")
        if con.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("foreign keys failed after ingestion")
        if con.execute("SELECT COUNT(*) FROM checkpoint_events").fetchone()[0]!=8:
            raise ValueError("checkpoint row count mismatch")
        if dict(con.execute("SELECT status,total FROM gate_counts"))!=DB.EXPECTED:
            raise ValueError("source gate statuses mutated")
        if con.execute("SELECT count(*) FROM checkpoint_events WHERE frame_attestation!='NOT_ADMITTED' OR depth_attestation!='NOT_RUN'").fetchone()[0]:
            raise ValueError("real frame or mesh illegally admitted")
        con.execute("VACUUM")
    out={
      "schema":"fab.visual.db.checkpoint-final-receipt.v0.1",
      "upstream_pin":DB.PIN,"reviewed_head":head,"ci_run_id":run_id,
      "original_db_snapshot_sha256":before_sha,
      "checkpoint_source_manifest_sha256":DB.digest(manifest_path.read_bytes()),
      "browser_receipt_sha256":DB.digest(browser_path.read_bytes()),
      "final_db_sha256":DB.digest(database.read_bytes()),
      "number_original_uninstrumented":4,
      "number_derivative_checkpoint_rows":8,
      "observer_state_snapshot_rows":4,
      "checkpoint_ordinal":3,
      "native_sheet_gate_status_authoritative":True,
      "gate_counts":DB.EXPECTED,
      "real_presented_frame":"NOT_ADMITTED",
      "real_geometry_depth":"NOT_RUN",
      "state_equivalence":"INCONCLUSIVE_UNCONTROLLED_RAF_TIME",
      "release":"HOLD","remote_server":"NOT_DEPLOYED"
    }
    receipt_path.parent.mkdir(parents=True,exist_ok=True)
    receipt_path.write_bytes(DB.canonical(out)+b"\n")
    return out


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--db",type=Path,required=True)
    a.add_argument("--manifest",type=Path,required=True)
    a.add_argument("--browser",type=Path,required=True)
    a.add_argument("--head-file",type=Path,required=True)
    a.add_argument("--run-id",type=int,required=True)
    a.add_argument("--receipt",type=Path,required=True)
    x=a.parse_args()
    print(json.dumps(ingest(x.db,x.manifest,x.browser,x.head_file,x.run_id,x.receipt),sort_keys=True))


if __name__=="__main__":
    main()
