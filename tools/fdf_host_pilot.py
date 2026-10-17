#!/usr/bin/env python3
"""R41 read-only before/after evidence integrity for a caller IDE pilot.

Does not run an IDE, inspect actual rendered meaning, approve a change, or
authenticate the witness or the operator who created the evidence.
"""
import argparse
import hashlib
import json
import os
import re
import stat
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.fdf_host_projectdna import build_host_binding
from tools.fdf_workspace_probe import _canonical_authorized_root, scan
from tools.fdf_proposal_compiler import stable_json

SCHEMA_BASELINE = "fdf.host.pilot-baseline/0.1"
SCHEMA_MANIFEST = "fdf.host.pilot-manifest/0.1"
SCHEMA_ADMISSION = "fdf.host.pilot-admission/0.1"
MAX_EVIDENCE_BYTES = 10 * 1024 * 1024
MAX_JSON_BYTES = 512 * 1024
REQUIRED_SHOTS = ("baseline_desktop", "after_desktop", "baseline_mobile", "after_mobile")
REQUIRED_CHECKS = ("build", "keyboard")


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _self_digest(data):
    return _digest(stable_json(data))


def capture(project, fdf_sha):
    host = build_host_binding(project, fdf_sha)
    observed = scan(project)
    if host["source_observation_sha256"] != _self_digest(observed):
        raise ValueError("HOLD: source changed during baseline capture")
    data = {
        "schema": SCHEMA_BASELINE,
        "fdf_source_commit": fdf_sha,
        "caller_root_sha256": _digest(str(_canonical_authorized_root(project)).encode("utf-8")),
        "policy_files": host["policy_files"],
        "policy_discovery_scope": host["policy_discovery_scope"],
        "baseline_admission": host["admission"],
        "coverage_admission": host["coverage_admission"],
        "observed_files": observed["observed_files"],
        "source_observation_sha256": host["source_observation_sha256"],
        "owner_authorized": False,
        "tests_executed": [],
        "host_master_witnessed": False,
        "release": "HOLD",
    }
    data["receipt_sha256"] = _self_digest(data)
    return data


def _evidence_bytes(root, relative, limit=MAX_EVIDENCE_BYTES):
    if not isinstance(relative, str) or not relative or len(relative) > 250:
        raise ValueError("HOLD: invalid evidence path")
    rel = Path(relative)
    if rel.is_absolute() or any(p in (".", "..", "") for p in rel.parts) or "\\" in relative or relative.startswith("/"):
        raise ValueError("HOLD: evidence traversal forbidden")
    target = root.joinpath(*rel.parts)
    for piece in (target, *[p for p in target.parents if p == root or root in p.parents]):
        if piece.is_symlink():
            raise ValueError("HOLD: symlink evidence path")
    try:
        fd = os.open(target, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(fd, "rb") as file:
            info = os.fstat(file.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
                raise ValueError("HOLD: nonregular or oversized evidence")
            data = file.read(limit + 1)
    except OSError as exc:
        raise ValueError("HOLD: unreadable evidence") from exc
    if len(data) > limit:
        raise ValueError("HOLD: oversized evidence")
    return data


def _json_file(root, name):
    try:
        value = json.loads(_evidence_bytes(root, name, MAX_JSON_BYTES).decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("HOLD: evidence JSON invalid") from exc
    if not isinstance(value, dict):
        raise ValueError("HOLD: evidence JSON object required")
    return value


def _file_record(root, record, kind):
    if not isinstance(record, dict) or set(record) != {"path", "sha256"}:
        raise ValueError("HOLD: invalid " + kind + " evidence entry")
    if not isinstance(record["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
        raise ValueError("HOLD: invalid artifact digest")
    data = _evidence_bytes(root, record["path"])
    if _digest(data) != record["sha256"]:
        raise ValueError("HOLD: " + kind + " artifact digest mismatch")
    return data


def _png_dimensions(data):
    """Check PNG framing, IHDR, IDAT, IEND and chunk CRCs, not rendered pixels.

    Even a structurally valid PNG may depict an unrelated or fabricated UI.
    """
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("HOLD: screenshot must be PNG")
    pos = 8
    chunks = 0
    dimensions = None
    idat_seen = False
    end_seen = False
    while pos < len(data):
        if chunks >= 256 or pos + 12 > len(data):
            raise ValueError("HOLD: PNG chunk count or framing invalid")
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        if length > MAX_EVIDENCE_BYTES or pos + 12 + length > len(data):
            raise ValueError("HOLD: PNG chunk oversized or truncated")
        content = data[pos + 8:pos + 8 + length]
        stored = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])[0]
        expected = zlib.crc32(kind + content) & 0xffffffff
        if stored != expected:
            raise ValueError("HOLD: PNG CRC mismatch")
        if chunks == 0:
            if kind != b"IHDR" or length != 13:
                raise ValueError("HOLD: PNG requires first 13-byte IHDR")
            width, height = struct.unpack(">II", content[:8])
            if not (240 <= width <= 8192 and 240 <= height <= 8192):
                raise ValueError("HOLD: screenshot dimensions outside bounded range")
            dimensions = [width, height]
        elif kind == b"IHDR":
            raise ValueError("HOLD: duplicate PNG IHDR")
        if kind == b"IDAT":
            idat_seen = True
        if kind == b"IEND":
            if length or not idat_seen or pos + 12 + length != len(data):
                raise ValueError("HOLD: PNG IEND missing IDAT or trailing bytes")
            end_seen = True
            break
        pos += 12 + length
        chunks += 1
    if not end_seen or dimensions is None:
        raise ValueError("HOLD: PNG missing final IEND")
    return dimensions

def admit(project, fdf_sha, evidence_dir, manifest_name):
    root = _canonical_authorized_root(evidence_dir)
    manifest = _json_file(root, manifest_name)
    if set(manifest) != {"schema", "fdf_source_commit", "baseline_receipt", "screenshots", "checks", "rollback"}:
        raise ValueError("HOLD: manifest keys incompatible")
    if manifest["schema"] != SCHEMA_MANIFEST or manifest["fdf_source_commit"] != fdf_sha:
        raise ValueError("HOLD: manifest schema or FDF source mismatch")
    baseline = _json_file(root, manifest["baseline_receipt"])
    receipt_sha = baseline.pop("receipt_sha256", None)
    if (baseline.get("schema") != SCHEMA_BASELINE
        or receipt_sha != _self_digest(baseline)
        or baseline.get("fdf_source_commit") != fdf_sha):
        raise ValueError("HOLD: invalid baseline integrity or source pin")
    if baseline.get("caller_root_sha256") != _digest(str(_canonical_authorized_root(project)).encode("utf-8")):
        raise ValueError("HOLD: baseline belongs to a different caller root")
    if baseline.get("owner_authorized") is not False or baseline.get("host_master_witnessed") is not False:
        raise ValueError("HOLD: baseline cannot assert authority or witness")
    if baseline.get("coverage_admission") != "PASS_SCOPED":
        raise ValueError("HOLD: incomplete baseline survey")
    if baseline.get("baseline_admission") != "SCOPED_PRECHECK_COMPLETE_HOST_MASTER_REVIEW_REQUIRED":
        raise ValueError("HOLD: baseline host-policy discovery insufficient")
    latest = build_host_binding(project, fdf_sha)
    if latest["coverage_admission"] != "PASS_SCOPED" or latest["admission"] != "SCOPED_PRECHECK_COMPLETE_HOST_MASTER_REVIEW_REQUIRED":
        raise ValueError("HOLD: current host intake incomplete")
    if latest["policy_files"] != baseline.get("policy_files"):
        raise ValueError("HOLD: host policy changed between baseline and admission")
    current = {x["path"]: x["sha256"] for x in scan(project)["observed_files"]}
    before = {x["path"]: x["sha256"] for x in baseline["observed_files"]}
    changed = sorted(p for p in set(before) | set(current) if before.get(p) != current.get(p))
    if not changed:
        raise ValueError("HOLD: no UI source difference from baseline")
    if len(changed) > 12:
        raise ValueError("HOLD: pilot exceeds bounded first-slice source scope")
    shots = manifest["screenshots"]
    checks = manifest["checks"]
    if not isinstance(shots, dict) or set(shots) != set(REQUIRED_SHOTS):
        raise ValueError("HOLD: desktop/mobile before/after screenshot pairs required")
    if not isinstance(checks, dict) or set(checks) != set(REQUIRED_CHECKS):
        raise ValueError("HOLD: explicit build and keyboard check artifacts required")
    dimensions = {}
    shot_digests = {}
    for label in REQUIRED_SHOTS:
        shot = shots[label]
        image = _file_record(root, shot, "screenshot")
        dimensions[label] = _png_dimensions(image)
        shot_digests[label] = shot["sha256"]
    for size in ("desktop", "mobile"):
        if dimensions["baseline_" + size] != dimensions["after_" + size]:
            raise ValueError("HOLD: comparison screenshot dimensions differ")
    if all(shot_digests["baseline_" + size] == shot_digests["after_" + size] for size in ("desktop", "mobile")):
        raise ValueError("HOLD: no visual artifact difference recorded")
    for name in REQUIRED_CHECKS:
        entry = checks[name]
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256", "reported_status"}:
            raise ValueError("HOLD: missing check record fields")
        if entry["reported_status"] != "PASS":
            raise ValueError("HOLD: check reported non-PASS")
        _file_record(root, {"path": entry["path"], "sha256": entry["sha256"]}, name)
    _file_record(root, manifest["rollback"], "rollback")
    return {
        "schema": SCHEMA_ADMISSION,
        "fdf_source_commit": fdf_sha,
        "changed_ui_source_paths": changed,
        "before_and_after_dimensions": dimensions,
        "artifacts_sha256": _self_digest(manifest),
        "checks": {name: "REPORTED_PASS_UNVERIFIED_EXECUTION" for name in REQUIRED_CHECKS},
        "admission": "ARTIFACT_BYTES_AND_POST_SOURCE_BOUNDED_CHECK_COMPLETE",
        "host_master_authority": "NOT_MACHINE_VERIFIED",
        "visual_design_quality": "NOT_EVALUATED",
        "keyboard_behavior": "NOT_REPLAYED",
        "host_test_execution": "NOT_REPLAYED",
        "source_repo_revision": "NOT_AUTHENTICATED_BY_TOOL",
        "real_ide_witness": "NOT_VERIFIED",
        "independent_approval": "HOLD",
        "release": "HOLD",
        "limitations": [
            "Evidence files and screenshots could be created or modified by the submitting operator.",
            "PNG header/digest checks do not show a real before/after browser session.",
            "Reported test logs are byte-checked, not independently executed.",
            "Historic baseline receipt is self-hashed, not independently authenticated.",
            "Only bounded eligible UI source changes and allowlisted host policy identities are measured.",
            "An independent human witness and actual host IDE examination are still required.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--fdf-sha", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--capture", action="store_true")
    mode.add_argument("--admit", help="manifest path relative to --evidence-dir")
    parser.add_argument("--evidence-dir", help="owner-controlled evidence folder outside caller app")
    args = parser.parse_args()
    try:
        if args.capture:
            answer = capture(args.project, args.fdf_sha)
        else:
            if not args.evidence_dir:
                raise ValueError("HOLD: --evidence-dir required for admission")
            answer = admit(args.project, args.fdf_sha, args.evidence_dir, args.admit)
        print(json.dumps(answer, indent=2, sort_keys=True))
    except (ValueError, KeyError, OSError, TypeError, UnicodeError) as exc:
        parser.exit(2, str(exc) + "\n")


if __name__ == "__main__":
    main()
