#!/usr/bin/env python3
"""Ω11H: immutable-native-Sheet snapshot -> append-only SQLite v0.2 candidate.

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
 "f9ad50dee5eb38481cd49cf6a3c2f6c9fd73799aa6f6f0fb2a931f881d1b23d1", # initial 32/35 build
 "c1d0a1293547183d4f22d1ee7d3b1026954c7a28ad066095de275e988267e693", # exact Ω11G final with 8
}
BASE_GATES=32
BASE_EVIDENCE=35
LATEST_IDS=[f"G11.{i}" for i in range(29,34)]
CURRENT_COUNTS={"PASS":19,"FAIL":6,"NOT_RUN":10,"HOLD":1,"INCONCLUSIVE":1}
RETAIN_FAIL=["G10.3","G11.14","G11.18","G11.21","G11.22","G11.28"]
ATTR=("gate_id","predicate","status","evidence_class","evidence_uri","change_authority","next_proof","implications")
EATTR=("title","scope","result","uri","limitations")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read_snapshot(path):
    raw=Path(path).read_bytes();data=json.loads(raw)
    if data.get("schema")!="fab.visual.native-gate-review-snapshot.v0.2":
        raise ValueError("source snapshot schema mismatch")
    if data.get("authority")!="NATIVE_SHEET_AUTHORITATIVE" or data.get("human_signature")!="NOT_PRESENT":
        raise ValueError("cannot fabricate signatures or invert native status authority")
    if data.get("provider_revision_token")!="NOT_AVAILABLE":
        raise ValueError("unsupported revision claim without provider evidence")
    if data.get("source_sheet")!=DB.SHEET:
        raise ValueError("wrong canonical native Sheet")
    if data.get("gate_range")!="Gate Registry!A7:H43" or data.get("evidence_range")!="Evidence Sources!A2:E45":
        raise ValueError("wrong source range")
    if data.get("baseline_db_sha256")!="c1d0a1293547183d4f22d1ee7d3b1026954c7a28ad066095de275e988267e693":
        raise ValueError("historic final DB anchor changed")
    gs=data.get("gates");es=data.get("evidence")
    if not isinstance(gs,list) or len(gs)!=37 or not isinstance(es,list) or len(es)!=44:
        raise ValueError("expected full native 37 gate/44 evidence source data")
    if any(set(g)!=set(ATTR) for g in gs) or any(set(e)!=set(EATTR) for e in es):
        raise ValueError("missing or extra native Sheet field")
    if len({g["gate_id"] for g in gs})!=37 or [g["gate_id"] for g in gs[32:]]!=LATEST_IDS:
        raise ValueError("unknown gate sequence or duplicate")
    if len({sha(DB.canonical(e)) for e in es})!=44:
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
        raise ValueError("baseline gate count not 32")
    by_id={r["gate_id"]:r for r in rows}
    if len(by_id)!=BASE_GATES or any(by_id.get(x["gate_id"])!=x for x in snapshot["gates"][:BASE_GATES]):
        raise ValueError("legacy gate row changed: refusing non-append reconciliation")
    old_e=[dict(zip(EATTR,r)) for r in con.execute("SELECT title,scope,result,uri,limitations FROM evidence ORDER BY rowid")]
    if len(old_e)!=BASE_EVIDENCE or old_e!=snapshot["evidence"][:BASE_EVIDENCE]:
        raise ValueError("legacy evidence row changed: refusing non-append reconciliation")
    prior_checkpoints=[r[0] for r in con.execute("SELECT checkpoint_id FROM checkpoint_events ORDER BY rowid")]
    n=len(prior_checkpoints)
    if n not in (0,8) or (old_sha==ALLOWED_BASE_SHA.__iter__().__next__() and n!=0):
        # The exact digest allowlist is checked; v0.1 has zero, Ω11G final has eight.
        raise ValueError("unexpected prior checkpoint count")
    if old_sha=="c1d0a1293547183d4f22d1ee7d3b1026954c7a28ad066095de275e988267e693" and n!=8:
        raise ValueError("eight prior verified checkpoints must survive")
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
            provenance="native-gate-sheet-v0.2-"+source_sha[:16]
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
                ("reconciliation_v0.2_snapshot_sha256",source_sha),
                ("reconciliation_v0.2_previous_db_sha256",old_sha),
                ("reconciliation_v0.2_grade","RESEARCH_SNAPSHOT_NO_CAS_NO_HUMAN_SIGNATURE"),
                ("reconciliation_v0.2_current_gate_range",snapshot["gate_range"]),
                ("reconciliation_v0.2_current_evidence_range",snapshot["evidence_range"]),
            ):
                con.execute("INSERT INTO metadata(key,value) VALUES (?,?)",(k,v))
            con.commit()
            after=[r[0] for r in con.execute("SELECT checkpoint_id FROM checkpoint_events ORDER BY rowid")]
            if after!=before:
                raise ValueError("prior derivative checkpoint evidence changed")
            counts=dict(con.execute("SELECT status,total FROM gate_counts"))
            if counts!=CURRENT_COUNTS or con.execute("SELECT count(*) FROM evidence").fetchone()[0]!=44:
                raise ValueError("post-import totals mismatch")
            if con.execute("SELECT count(*) FROM ci_runs").fetchone()[0]!=(2 if len(before)==0 else 3):
                raise ValueError("prior CI lineage corrupted")
            if con.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or con.execute("PRAGMA foreign_key_check").fetchall():
                raise ValueError("post-import SQLite damaged")
            con.execute("VACUUM")
        if sha(source_db.read_bytes())!=old_sha:
            raise ValueError("immutable input unexpectedly changed")
        receipt={
          "schema":"fab.visual.db.reconciliation-receipt.v0.2",
          "source_sheet":DB.SHEET,"sheet_modified_time_at_read":snapshot["sheet_modified_time_at_read"],
          "provider_revision":"NOT_AVAILABLE","human_signature":"NOT_PRESENT",
          "authority":"NATIVE_SHEET_AUTHORITATIVE","admission":"RESEARCH_SNAPSHOT_ONLY",
          "native_snapshot_sha256":source_sha,"baseline_db_sha256":old_sha,
          "candidate_db_sha256":sha(output_db.read_bytes()),
          "historical_gates_preserved":32,"new_gates":5,"total_gates":37,
          "historical_evidence_preserved":35,"new_evidence":9,"total_evidence":44,
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
    a.add_argument("--snapshot",type=Path,default=HERE/"native_snapshot_2026-11-14_v0.2.json")
    a.add_argument("--output",type=Path,required=True)
    a.add_argument("--receipt",type=Path,required=True)
    args=a.parse_args()
    print(json.dumps(reconcile(args.input,args.snapshot,args.output,args.receipt),sort_keys=True))


if __name__=="__main__":
    main()
