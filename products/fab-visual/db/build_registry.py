#!/usr/bin/env python3
"""FAB.VISUAL portable SQLite constitutional evidence DB v0.1.

Native Google Sheets Gate Registry remains the authority for gate status.
This file builds a deterministic, append-only, offline research snapshot.
No cloud service, database server, host or live bidirectional sync is enabled.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parent
PIN="1482e8469b0a9e0d8cc18ea2740a01423d29ae80"
SHEET="https://docs.google.com/spreadsheets/d/1Hn8MoTf-AFbcIZuQyskBneo4iPnA9y00HJWUrGJqn7M/edit"
EXPECTED={"PASS":16,"FAIL":6,"NOT_RUN":9,"HOLD":1}
STATUSES=frozenset(("PASS","FAIL","NOT_RUN","HOLD","INCONCLUSIVE"))


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_seed(path):
    raw=Path(path).read_bytes()
    seed=json.loads(raw)
    if seed.get("schema")!="fab.visual.db.seed.v0.1":
        raise ValueError("wrong source seed schema")
    if seed.get("canonical_authority")!="NATIVE_SHEET_IS_SOURCE_OF_CURRENT_GATE_STATUSES":
        raise ValueError("lost authority boundary")
    if seed.get("no_automatic_bidirectional_sync") is not True:
        raise ValueError("automatic sync cannot be enabled by seed")
    src=seed.get("original_upstream",{})
    if src.get("commit")!=PIN or src.get("locked_blobs")!=173:
        raise ValueError("untrusted original Anatomy revision")
    if seed.get("gate_sheet_source",{}).get("url")!=SHEET:
        raise ValueError("untrusted native gate sheet")
    if seed.get("evidence_sheet_source",{}).get("url")!=SHEET:
        raise ValueError("untrusted native evidence sheet")
    gates=seed.get("gates")
    if not isinstance(gates,list) or len(gates)!=32:
        raise ValueError("expected 32 source gate records for v0.1")
    if len({g.get("gate_id") for g in gates})!=len(gates):
        raise ValueError("duplicate source gate ID")
    count={s:sum(g.get("status")==s for g in gates) for s in EXPECTED}
    if count!=EXPECTED:
        raise ValueError("gate totals changed without new source snapshot")
    if any(g.get("status") not in STATUSES for g in gates):
        raise ValueError("unrecognized gate status")
    if not isinstance(seed.get("evidence"),list) or len(seed["evidence"])!=35:
        raise ValueError("expected 35 source evidence records")
    if next(g for g in gates if g["gate_id"]=="G11.12")["status"]!="HOLD":
        raise ValueError("release HOLD must be preserved")
    return seed


def build(seed_path, schema_path, out_db, out_manifest):
    seed_path=Path(seed_path)
    schema_path=Path(schema_path)
    out_db=Path(out_db)
    out_manifest=Path(out_manifest)
    seed=read_seed(seed_path)
    schema_bytes=schema_path.read_bytes()
    if not schema_bytes.startswith(b"-- FAB.VISUAL constitutional central database"):
        raise ValueError("unexpected schema")
    if out_db.exists() or out_manifest.exists():
        raise ValueError("refuse to overwrite existing DB or receipt")
    out_db.parent.mkdir(parents=True,exist_ok=True)
    out_manifest.parent.mkdir(parents=True,exist_ok=True)
    # Avoid shared mutable DB references. Only one new snapshot per CI checkout.
    con=sqlite3.connect(out_db)
    try:
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript(schema_bytes.decode("utf8"))
        con.execute("BEGIN IMMEDIATE")
        sources=[
          ("original-anatomy","UPSTREAM_GIT",
           "https://github.com/wheresryan22/anatomy",PIN,None,"ORIGINAL_IMMUTABLE"),
          ("native-gate-sheet","NATIVE_SHEET",SHEET,"Gate Registry!A7:H38",None,"SHEET_AUTHORITATIVE"),
          ("native-evidence-sheet","NATIVE_SHEET",SHEET,"Evidence Sources!A2:E36",None,"SHEET_AUTHORITATIVE"),
          ("research-pr31","GITHUB","https://github.com/Ivan-Pasev/fabrica-design-fabric/pull/31",
           seed["research_head"],None,"EVIDENCE_REFERENCE")
        ]
        con.executemany("""INSERT INTO sources
          (source_id,kind,uri,pinned_revision,sha256,authority)
          VALUES (?,?,?,?,?,?)""",sources)
        for key,value in (
          ("schema_version","v0.1"),("authority","NATIVE_SHEET_IS_SOURCE_OF_CURRENT_GATE_STATUSES"),
          ("release","HOLD"),("actual_renderer_frame","NOT_ADMITTED"),
          ("real_mesh_geometry","NOT_RUN"),("source_gate_range","Gate Registry!A7:H38"),
          ("source_evidence_range","Evidence Sources!A2:E36"),
          ("seed_sha256",digest(seed_path.read_bytes())),
          ("sql_schema_sha256",digest(schema_bytes)),
          ("capture_date",seed["captured_as_of"])
        ):
            con.execute("INSERT INTO metadata(key,value) VALUES (?,?)",(key,value))
        for gate in seed["gates"]:
            payload={"gate":gate,"ordinal":1,"source_id":"native-gate-sheet"}
            event_id=digest(canonical(payload))
            con.execute("""INSERT INTO gate_events(
              event_id,gate_id,ordinal,status,predicate,evidence_class,
              evidence_uri,change_authority,next_proof,implications,source_id,captured_as_of)
              VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
              (event_id,gate["gate_id"],1,gate["status"],gate["predicate"],
               gate["evidence_class"],gate["evidence_uri"],gate["change_authority"],
               gate["next_proof"],gate["implications"],"native-gate-sheet",
               seed["captured_as_of"]))
        for record in seed["evidence"]:
            event_id=digest(canonical({"evidence":record,"source_id":"native-evidence-sheet"}))
            con.execute("""INSERT INTO evidence(
              evidence_id,title,scope,result,uri,limitations,source_id)
              VALUES (?,?,?,?,?,?,?)""",
              (event_id,record["title"],record["scope"],record["result"],
               record["uri"],record["limitations"],"native-evidence-sheet"))
        for run in seed["ci_runs"]:
            if run["result"]!="PASS" or run["grade"]!="INSTRUMENTED_DERIVATIVE" or run["release"]!="HOLD":
                raise ValueError("unexpected CI classification in seed")
            con.execute("""INSERT INTO ci_runs
             (run_id,source_head,original_pin,github_uri,result,grade,release,provenance_source_id)
             VALUES (?,?,?,?,?,?,?,?)""",
             (run["run_id"],run["source_head"],PIN,
              f"https://github.com/Ivan-Pasev/fabrica-design-fabric/actions/runs/{run['run_id']}",
              run["result"],run["grade"],run["release"],"research-pr31"))
        con.commit()
        if con.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("SQLite integrity check failed")
        if con.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("SQLite referential integrity failed")
        actual={k:v for k,v in con.execute("SELECT status,total FROM gate_counts")}
        if actual!=EXPECTED:
            raise ValueError("gate count mismatch")
        if con.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]!=35:
            raise ValueError("evidence count mismatch")
        if con.execute("SELECT COUNT(*) FROM checkpoint_events").fetchone()[0]!=0:
            raise ValueError("unexpected fabricated checkpoint evidence")
        con.execute("VACUUM")
    except Exception:
        con.close()
        out_db.unlink(missing_ok=True)
        raise
    con.close()
    out={
      "schema":"fab.visual.db.snapshot-receipt.v0.1",
      "source_seed_sha256":digest(seed_path.read_bytes()),
      "source_schema_sha256":digest(schema_bytes),
      "database_sha256":digest(out_db.read_bytes()),
      "source_commit":PIN,
      "upstream_source_integrity":"PREVIOUSLY_VERIFIED_CI_SOURCE_PIN",
      "sheet_source":SHEET,
      "sheet_authoritative_for_current_gate_status":True,
      "live_bidirectional_sync":"NOT_IMPLEMENTED",
      "tables":["metadata","sources","gate_events","evidence","ci_runs","checkpoint_events"],
      "source_gate_count":32,"source_evidence_count":35,
      "checkpoint_event_count":0,
      "status_counts":EXPECTED,
      "frame_attestation":"NOT_ADMITTED","real_mesh_depth":"NOT_RUN",
      "release":"HOLD",
      "network_server":"NOT_DEPLOYED",
      "read_only_snapshot":True
    }
    out_manifest.write_bytes(canonical(out)+b"\n")
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--seed",type=Path,default=ROOT/"canonical_seed_2026-11-14.json")
    ap.add_argument("--schema",type=Path,default=ROOT/"schema.sql")
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--receipt",type=Path,required=True)
    args=ap.parse_args()
    print(json.dumps(build(args.seed,args.schema,args.output,args.receipt),sort_keys=True))


if __name__=="__main__":
    main()
