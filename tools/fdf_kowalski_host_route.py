#!/usr/bin/env python3
"""FDF/EK-002: host-bound, read-only selection of pinned upstream design refs.

This module never executes an IDE, fetches external instructions, changes source,
or authenticates owner consent. A ProjectDNA hash does not prove policy compliance.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Allow direct invocation from a read-only FDF checkout.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.fdf_host_projectdna import build_host_binding, verify_host_binding
from tools.fdf_host_operator_gate import evaluate as evaluate_operator
from tools.fdf_kowalski_bridge import route

SCHEMA = "fdf.kbi.ek-host-route/0.1"
HOST_PRECHECK_OK = "SCOPED_PRECHECK_COMPLETE_HOST_MASTER_REVIEW_REQUIRED"
DESIGN_OPS = frozenset({"NEXT", "REVIEW", "REFINE"})


def plan_for_host(project, fdf_sha, framework, intent, host_operator="NEXT(UX)",
                  *, explicit=False, previous_host_receipt=None):
    """Bind a reference selection to the *fresh* caller ProjectDNA admission.

    The operator snapshot is advisory; the host's actual instructions have to
    be interpreted by the live master agent, outside this module.
    """
    if not isinstance(fdf_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", fdf_sha):
        raise ValueError("HOLD: exact 40-character lowercase FDF source pin required")
    if not isinstance(host_operator, str) or len(host_operator) > 90:
        raise ValueError("HOLD: invalid host operator")
    assessment = evaluate_operator({
        "operator": host_operator,
        "host_sha": "NOT_VERIFIED",
        "pending": None,
        "accepted_proposal_id": None,
    })
    result = {
        "schema": SCHEMA,
        "mode": "PROPOSE_ONLY",
        "operator": host_operator,
        "operator_advice": assessment["verdict"],
        "operator_is_authenticated": False,
        "actual_ide_executed": False,
        "host_policy_semantics_checked": False,
        "owner_authorized": False,
        "writes_performed": False,
        "dependencies_installed": False,
        "upstream_source_downloaded": False,
        "framework_claim_verified": False,
        "fdf_source_commit": fdf_sha,
        "fdf_commit_verified_by_tool": False,
        "host_projectdna_receipt_sha256": None,
        "host_projectdna_admission": "NOT_EXECUTED",
        "coverage_admission": "NOT_EXECUTED",
        "skill_route": None,
        "status": "HOLD",
        "release": "HOLD",
    }
    # No caller-source read for forbidden/implementation operators.
    if (assessment["verdict"] != "HOST_READ_ONLY_OPERATOR" or
            assessment["normalized_operator"] not in DESIGN_OPS):
        result["status"] = "HOLD_HOST_OPERATOR_NOT_DESIGN_PROPOSAL"
        return result

    host = (verify_host_binding(project, previous_host_receipt)
            if previous_host_receipt is not None
            else build_host_binding(project, fdf_sha))
    if host.get("fdf_source_commit") != fdf_sha:
        raise ValueError("HOLD: stale FDF source pin in host ProjectDNA")
    result["host_projectdna_receipt_sha256"] = host["receipt_sha256"]
    result["host_projectdna_admission"] = host["admission"]
    result["coverage_admission"] = host["coverage_admission"]
    result["host_ui_observed_files"] = host["ui_observed_files"]
    result["host_policy_file_count"] = len(host["policy_files"])
    result["host_source_git_commit"] = host["host_source_git_commit"]
    result["host_observation_sha256"] = host["source_observation_sha256"]
    if host["admission"] != HOST_PRECHECK_OK:
        result["status"] = "HOLD_HOST_PROJECTDNA_PRECHECK"
        return result

    selected = route(framework, intent, explicit=explicit, project_known=True)
    result["skill_route"] = selected
    if selected["status"] != "REFERENCE_SELECTED_PROPOSAL_ONLY":
        result["status"] = selected["status"]
        return result
    result["status"] = "REFERENCE_SELECTED_HOST_PRECHECK_ONLY"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True,
                        help="Explicitly approved read-only caller project root")
    parser.add_argument("--fdf-sha", required=True, help="Exact reviewed FDF commit")
    parser.add_argument("--framework", required=True,
                        choices=["web", "react", "nextjs", "expo", "swift", "unknown"])
    parser.add_argument("--intent", required=True)
    parser.add_argument("--host-operator", default="NEXT(UX)")
    parser.add_argument("--explicit-user-invocation", action="store_true")
    args = parser.parse_args()
    try:
        result = plan_for_host(
            args.project, args.fdf_sha, args.framework, args.intent,
            args.host_operator, explicit=args.explicit_user_invocation
        )
        print(json.dumps(result, indent=2, sort_keys=True))
    except (ValueError, OSError, TypeError) as e:
        parser.exit(2, str(e) + "\n")


if __name__ == "__main__":
    main()
