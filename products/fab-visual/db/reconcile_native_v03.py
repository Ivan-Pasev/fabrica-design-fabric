#!/usr/bin/env python3
"""Ω11I: source-bound v0.2 -> append-only SQLite v0.3 candidate.

No network, no unverified signature, no concurrent Google Sheets CAS, no
production authority. Applies only after validating all 32 + 35 old records
against a source-grounded full 37 + 44 snapshot, and never mutates input.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3

HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("fab11h_builder",HERE/"build_registry.py")
DB=importlib.util.module_from_spec(sp);sp.loader.exec_module(DB)
ALLOWED_BASE_SHA={
 "c54ee65951058f7ada58ce61e6cf3807f605620b244461808596677e6dce360e", # exact Ω11H v0.2 37/44/8
}
BASE_GATES=37
BASE_EVIDENCE=44
LATEST_IDS=[f"G11.{i}" for i in range(34,40)]
CURRENT_COUNTS={"PASS":23,"FAIL":6,"NOT_RUN":11,"HOLD":1,"INCONCLUSIVE":2}
RETAIN_FAIL=["G10.3","G11.14","G11.18","G11.21","G11.22","G11.28"]
ATTR=("gate_id","predicate","status","evidence_class","evidence_uri","change_authority","next_proof","implications")
EATTR=("title","scope","result","uri","limitations")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read_snapshot(path):
    raw=Path(path).read_bytes();data=json.loads(raw)
    if data.get("schema")!="fab.visual.native-gate-review-snapshot.v0.3":
        raise ValueError("source snapshot schema mismatch")
    if data.get("authority")!="NATIVE_SHEET_AUTHORITATIVE" or data.get("human_signature")!="NOT_PRESENT":
        raise ValueError("cannot fabricate signatures or invert native status authority")
    if data.get("provider_revision_token")!="NOT_AVAILABLE":
        raise ValueError("unsupported revision claim without provider evidence")
    if data.get("source_sheet")!=DB.SHEET:
        raise ValueError("wrong canonical native Sheet")
    if data.get("gate_range")!="Gate Registry!A7:H49" or data.get("evidence_range")!="Evidence Sources!A2:E53":
        raise ValueError("wrong source range")
    if data.get("baseline_db_sha256")!="c54ee65951058f7ada58ce61e6cf3807f605620b244461808596677e6dce360e":
        raise ValueError("historic final DB anchor changed")
    gs=data.get("gates");es=data.get("evidence")
    if not isinstance(gs,list) or len(gs)!=43 or not isinstance(es,list) or len(es)!=52:
        raise ValueError("expected complete 43 gate/52 evidence source data")
    if any(set(g)!=set(ATTR) for g in gs) or any(set(e)!=set(EATTR) for e in es):
        raise ValueError("missing or extra native Sheet field")
    if len({g["gate_id"] for g in gs})!=43 or [g["gate_id"] for g in gs[BASE_GATES:]]!=LATEST_IDS:
        raise ValueError("unknown gate sequence or duplicate")
    if len({sha(DB.canonical(e)) for e in es})!=52:
        raise ValueError("duplicated native evidence record")
    counts={s:sum(g["status"]==s for g in gs) for s in CURRENT_COUNTS}
    if counts!=CURRENT_COUNTS or counts!=data.get("expected_counts"):
        raise ValueError("native gate status count mismatch")
    if any(g["status"] not in DB.STATUSES for g in gs):
        raise ValueError("unsupported status")
    for k in RETAIN_FAIL:
        if next(x for x in gs if x["gate_id"]==k)["status"]!="FAIL":
            raise ValueError("historical FAIL status laundering")
    if next(x for x in gs if x["gate_id"]=="G11.12")["status"]!="HOLD":
        raise ValueError("release authority was silently promoted")
    if next(x for x in gs if x["gate_id"]=="G11.32")["status"]!="INCONCLUSIVE":
        raise ValueError("uncontrolled RAF equivalence wrongly promoted")
    if next(x for x in gs if x["gate_id"]=="G11.33")["status"]!="NOT_RUN":
        raise ValueError("managed DB service/sync wrongly promoted")
    if next(x for x in gs if x["gate_id"]=="G11.38")["status"]!="INCONCLUSIVE":
        raise ValueError("test-clock equivalence wrongly promoted")
    if next(x for x in gs if x["gate_id"]=="G11.39")["status"]!="NOT_RUN":
        raise ValueError("real geometry/presented-frame falsely certified")
    if data.get("release")!="HOLD" or data.get("revision_integrity")!="READ_ONLY_MODIFIED_TIME_NOT_CAS":
        raise ValueError("source snapshot claims unapproved release or revision authority")
    return data,sha(raw)


def verify_baseline(con,old_sha,snapshot):
    if old_sha not in ALLOWED_BASE_SHA:
        raise ValueError("unrecognized immutable base DB digest")
    if con.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or con.execute("PRAGMA foreign_key_check").fetchall():
        raise ValueError("damaged existing SQLite base")
    md=dict(con.execute("SELECT key,value FROM metadata"))
    if md.get("release")!="HOLD" or md.get("actual_renderer_frame")!="NOT_ADMITTED" or md.get("real_mesh_geometry")!="NOT_RUN":
        raise ValueError("legacy constitutional claim boundary changed")
    rows=[dict(zip(ATTR,r)) for r in con.execute(
      "SELECT gate_id,predicate,status,evidence_class,evidence_uri,change_authority,next_proof,implications FROM gate_current ORDER BY rowid")]
    if len(rows)!=BASE_GATES:
        raise ValueError("baseline gate count not 37")
    by_id={r["gate_id"]:r for r in rows}
    if len(by_id)!=BASE_GATES or any(by_id.get(x["gate_id"])!=x for x in snapshot["gates"][:BASE_GATES]):
        raise ValueError("legacy gate row changed: refusing non-append reconciliation")
    old_e=[dict(zip(EATTR,r)) for r in con.execute("SELECT title,scope,result,uri,limitations FROM evidence ORDER BY rowid")]
    if len(old_e)!=BASE_EVIDENCE or old_e!=snapshot["evidence"][:BASE_EVIDENCE]:
        raise ValueError("legacy evidence row changed: refusing non-append reconciliation")
    prior_checkpoints=[r[0] for r in con.execute("SELECT checkpoint_id FROM checkpoint_events ORDER BY rowid")]
    n=len(prior_checkpoints)
    if n!=8:
        raise ValueError("eight prior source-verified checkpoints must survive")
    return prior_checkpoints


def reconcile(source_db,snapshot_path,output_db,receipt_path):
    source_db=Path(source_db);output_db=Path(output_db);receipt_path=Path(receipt_path)
    if not source_db.is_file() or output_db.exists() or receipt_path.exists():
        raise ValueError("base must exist; destination and receipt must not exist")
    if source_db.resolve()==output_db.resolve():
        raise ValueError("forbidden in-place edit of archived central database")
    snapshot,source_sha=read_snapshot(snapshot_path)
    old_raw=source_db.read_bytes()
    old_sha=sha(old_raw)
    if old_sha not in ALLOWED_BASE_SHA:
        raise ValueError("base digest not in exact audited allowlist")
    output_db.parent.mkdir(parents=True,exist_ok=True);receipt_path.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source_db,output_db)
    try:
        with sqlite3.connect(output_db) as con:
            con.execute("PRAGMA foreign_keys=ON")
            before=verify_baseline(con,old_sha,snapshot)
            provenance="native-gate-sheet-v0.3-"+source_sha[:16]
            con.execute("BEGIN IMMEDIATE")
            con.execute("""INSERT INTO sources(source_id,kind,uri,pinned_revision,sha256,authority)
                         VALUES(?,?,?,?,?,?)""",(provenance,"NATIVE_SHEET",DB.SHEET,
                    snapshot["sheet_modified_time_at_read"]+"|"+snapshot["gate_range"]+"|"+snapshot["evidence_range"],
                    source_sha,"SHEET_AUTHORITATIVE"))
            for g in snapshot["gates"][BASE_GATES:]:
                event_id=sha(DB.canonical({"gate":g,"ordinal":1,"source_id":provenance}))
                con.execute("""INSERT INTO gate_events
                    (event_id,gate_id,ordinal,status,predicate,evidence_class,evidence_uri,change_authority,next_proof,implications,source_id,captured_as_of)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (event_id,g["gate_id"],1,g["status"],g["predicate"],g["evidence_class"],
                     g["evidence_uri"],g["change_authority"],g["next_proof"],g["implications"],provenance,
                     snapshot["snapshot_date"]))
            for e in snapshot["evidence"][BASE_EVIDENCE:]:
                event_id=sha(DB.canonical({"evidence":e,"source_id":provenance}))
                con.execute("""INSERT INTO evidence(evidence_id,title,scope,result,uri,limitations,source_id)
                    VALUES (?,?,?,?,?,?,?)""",(event_id,e["title"],e["scope"],e["result"],
                         e["uri"],e["limitations"],provenance))
            for k,v in (
                ("reconciliation_v0.3_snapshot_sha256",source_sha),
                ("reconciliation_v0.3_previous_db_sha256",old_sha),
                ("reconciliation_v0.3_grade","RESEARCH_SNAPSHOT_NO_CAS_NO_HUMAN_SIGNATURE"),
                ("reconciliation_v0.3_current_gate_range",snapshot["gate_range"]),
                ("reconciliation_v0.3_current_evidence_range",snapshot["evidence_range"]),
            ):
                con.execute("INSERT INTO metadata(key,value) VALUES (?,?)",(k,v))
            con.commit()
            after=[r[0] for r in con.execute("SELECT checkpoint_id FROM checkpoint_events ORDER BY rowid")]
            if after!=before:
                raise ValueError("prior derivative checkpoint evidence changed")
            counts=dict(con.execute("SELECT status,total FROM gate_counts"))
            if counts!=CURRENT_COUNTS or con.execute("SELECT count(*) FROM evidence").fetchone()[0]!=52:
                raise ValueError("post-import totals mismatch")
            if con.execute("SELECT count(*) FROM ci_runs").fetchone()[0]!=3:
                raise ValueError("prior CI lineage corrupted")
            if con.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or con.execute("PRAGMA foreign_key_check").fetchall():
                raise ValueError("post-import SQLite damaged")
            con.execute("VACUUM")
        if sha(source_db.read_bytes())!=old_sha:
            raise ValueError("immutable input unexpectedly changed")
        receipt={
          "schema":"fab.visual.db.reconciliation-receipt.v0.3",
          "source_sheet":DB.SHEET,"sheet_modified_time_at_read":snapshot["sheet_modified_time_at_read"],
          "provider_revision":"NOT_AVAILABLE","human_signature":"NOT_PRESENT",
          "authority":"NATIVE_SHEET_AUTHORITATIVE","admission":"RESEARCH_SNAPSHOT_ONLY",
          "native_snapshot_sha256":source_sha,"baseline_db_sha256":old_sha,
          "candidate_db_sha256":sha(output_db.read_bytes()),
          "historical_gates_preserved":37,"new_gates":6,"total_gates":43,
          "historical_evidence_preserved":44,"new_evidence":8,"total_evidence":52,
          "checkpoint_ids_preserved":len(before),
          "gate_counts":CURRENT_COUNTS,
          "frame_attestation":"NOT_ADMITTED","real_geometry":"NOT_RUN",
          "live_sync":"NOT_IMPLEMENTED","release":"HOLD"
        }
        receipt_path.write_bytes(DB.canonical(receipt)+b"\n")
        return receipt
    except Exception:
        output_db.unlink(missing_ok=True)
        raise


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--input",type=Path,required=True)
    a.add_argument("--snapshot",type=Path,default=HERE/"native_snapshot_2026-11-14_v0.3.json")
    a.add_argument("--output",type=Path,required=True)
    a.add_argument("--receipt",type=Path,required=True)
    args=a.parse_args()
    print(json.dumps(reconcile(args.input,args.snapshot,args.output,args.receipt),sort_keys=True))


if __name__=="__main__":
    main()
