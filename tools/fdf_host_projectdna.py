#!/usr/bin/env python3
"""R40 read-only host ProjectDNA admission receipt.

This program measures a narrow policy/source inventory; it does not parse,
obey or enforce host rules, execute an IDE, validate FDF provenance or approve
a design edit. JSON digests are local integrity evidence, not attestations.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# Allow direct python3 tools/fdf_host_projectdna.py invocation from any cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.fdf_workspace_probe import _bounded_regular_file, _canonical_authorized_root, scan
from tools.fdf_proposal_compiler import compile_plan, stable_json

POLICY_PATHS = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "AI_CRITICAL.md",
    ".cursorrules",
    ".github/copilot-instructions.md",
)
SCHEMA = "fdf.host.projectdna-admission/0.1"
SOURCE_ROOT = Path(__file__).resolve().parents[1]


def _policy_evidence(root, relative):
    path = root / relative
    # This fixed allowlist does not enumerate other files or read secrets.
    if not path.exists() and not path.is_symlink():
        return None
    if any(p.is_symlink() for p in (path, *[x for x in path.parents if x == root or root in x.parents])):
        return {"path": relative, "status": "HOLD_SYMLINK", "sha256": None}
    data, error = _bounded_regular_file(path)
    if error:
        return {"path": relative, "status": "HOLD_" + error.upper(), "sha256": None}
    return {
        "path": relative,
        "status": "DIGEST_ONLY_NOT_SEMANTICALLY_READ",
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def build_host_binding(project, fdf_commit):
    if not isinstance(fdf_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", fdf_commit):
        raise ValueError("HOLD: require an exact lower-case 40-character FDF commit SHA")
    root = _canonical_authorized_root(project)
    if root == SOURCE_ROOT:
        raise ValueError("HOLD: target is FDF source, not the caller workspace")
    policies = [
        item for relative in POLICY_PATHS
        if (item := _policy_evidence(root, relative)) is not None
    ]
    observed = scan(root)
    proposed = compile_plan(root, observed)
    coverage = proposed["coverage_binding"]["current_scan"]
    if not policies:
        outcome = "HOLD_HOST_POLICY_DISCOVERY_UNKNOWN"
    elif any(item["status"].startswith("HOLD_") for item in policies):
        outcome = "HOLD_POLICY_UNREADABLE"
    elif proposed["coverage_admission"] != "PASS_SCOPED":
        outcome = "HOLD_SOURCE_COVERAGE"
    elif not observed["observed_files"]:
        outcome = "HOLD_NO_UI_FILES_OBSERVED"
    else:
        outcome = "SCOPED_PRECHECK_COMPLETE_HOST_MASTER_REVIEW_REQUIRED"
    record = {
        "schema": SCHEMA,
        "target": "CALLER_IDE_ACTIVE_WORKSPACE",
        "mode": "PROPOSE_ONLY",
        "fdf_source_commit": fdf_commit,
        "fdf_commit_verified_by_tool": False,
        "host_source_git_commit": "NOT_DETERMINED",
        "policy_discovery_scope": list(POLICY_PATHS),
        "policy_files": policies,
        "host_policy_semantics": "NOT_READ_OR_ENFORCED_BY_THIS_TOOL",
        "host_master_authority": "REQUIRES_ACTUAL_IDE_AGENT_REVIEW",
        "source_observation_sha256": hashlib.sha256(stable_json(observed)).hexdigest(),
        "proposal_sha256": hashlib.sha256(stable_json(proposed)).hexdigest(),
        "ui_observed_files": len(observed["observed_files"]),
        "candidate_ui_findings": len(observed["candidate_changes"]),
        "source_coverage": coverage,
        "coverage_admission": proposed["coverage_admission"],
        "admission": outcome,
        "automated_edits": False,
        "owner_authorized": False,
        "runtime_checks_executed": [],
        "visual_evidence": "NOT_EXECUTED",
        "real_caller_ide_witness": "NOT_VERIFIED",
        "release": "HOLD",
        "limitations": [
            "Allowlisted root policy-file digests are not semantic authority checks.",
            "Nested/IDE-specific/global policies outside the allowlist may apply.",
            "A supplied FDF SHA has not been authenticated by this local tool.",
            "Source scope is limited by the preexisting heuristic scanner.",
            "No actual host render, keyboard, build, performance or end-to-end IDE trial ran.",
        ],
    }
    record["receipt_sha256"] = hashlib.sha256(stable_json(record)).hexdigest()
    return record


def verify_host_binding(project, record):
    if not isinstance(record, dict) or record.get("schema") != SCHEMA:
        raise ValueError("HOLD: incompatible host receipt schema")
    fresh = build_host_binding(project, record.get("fdf_source_commit"))
    if record != fresh:
        raise ValueError("HOLD: host policies, UI source or receipt fields stale or forged")
    return fresh


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--fdf-sha", required=True)
    parser.add_argument("--verify", help="Read-only verification of an existing receipt")
    args = parser.parse_args()
    try:
        if args.verify:
            receipt = Path(args.verify)
            if receipt.is_symlink() or not receipt.is_file() or receipt.stat().st_size > 512 * 1024:
                raise ValueError("HOLD: untrusted or oversized receipt path")
            data = json.loads(receipt.read_text(encoding="utf-8"))
            if data.get("fdf_source_commit") != args.fdf_sha:
                raise ValueError("HOLD: requested source pin differs")
            answer = verify_host_binding(args.project, data)
        else:
            answer = build_host_binding(args.project, args.fdf_sha)
        print(json.dumps(answer, indent=2, sort_keys=True))
    except (ValueError, OSError, TypeError, UnicodeError) as exc:
        parser.exit(2, str(exc) + "\n")


if __name__ == "__main__":
    main()
