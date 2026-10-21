#!/usr/bin/env python3
"""Read-only, source-grounded FDF third-party portfolio inspection and fit routing.

No repository cloning, dependency installation, source writes, policy changes or
remote execution. Registry observations are historical, not current HEAD checks.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "third_party_sources.v1.json"
EMIL = ROOT / "registry" / "upstream-emil-kowalski.v1.json"
INTENTS = {
    "design": {"design", "components"},
    "motion": {"motion"},
    "spatial": {"spatial"},
    "quality": {"quality"},
    "mobile": {"mobile"},
    "tokens": {"tokens"},
    "runtime": {"runtime"},
    "components": {"components"},
}
BLOCKED_LICENSE = {"LICENSE_UNKNOWN", "REDISTRIBUTION_RESTRICTED", "MIXED_SUBPATH_REVIEW", "SUBPATH_REVIEW_REQUIRED"}
BLOCKED_DISTRIBUTION = {"DO_NOT_BUNDLE"}
ALLOWED = set().union(*INTENTS.values())


def load(path: pathlib.Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 256_000:
        raise ValueError("HOLD: missing, linked, or oversized registry")
    return json.loads(path.read_text(encoding="utf-8"))


def audit(registry: dict | None = None, emil: dict | None = None) -> dict:
    reg = registry if registry is not None else load(REGISTRY)
    ek = emil if emil is not None else load(EMIL)
    records = reg.get("repositories")
    if reg.get("schema") != "fdf.portfolio.third_party_sources/1.0.0":
        raise ValueError("HOLD: incompatible portfolio schema")
    if not isinstance(records, list) or len(records) != 30:
        raise ValueError("HOLD: unexpected portfolio cardinality")
    names = [r.get("repo") for r in records]
    if len(set(names)) != 30 or not all(isinstance(n, str) and "/" in n for n in names):
        raise ValueError("HOLD: malformed or duplicate repository")
    for r in records:
        if not isinstance(r.get("capabilities"), list) or not set(r["capabilities"]) <= ALLOWED:
            raise ValueError("HOLD: invalid capability tags")
        if r.get("installed_in_owner_ide") is not False or r.get("owner_approved_install") is not False or r.get("host_verified") is not False:
            raise ValueError("HOLD: registry improperly asserts installer/host approval")
        if r.get("distribution") != "NO_PUBLIC_UPSTREAM_CODE_BUNDLED":
            raise ValueError("HOLD: unauthorized upstream redistribution claim")
        commit = r.get("source_commit")
        if commit is not None and (not isinstance(commit, str) or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit)):
            raise ValueError("HOLD: malformed historical source pin")
        if r["license_gate"] in BLOCKED_LICENSE and r["disposition"] == "INSTALL_AUTHORIZED":
            raise ValueError("HOLD: license gate bypass")
    if ek.get("upstream", {}).get("repo") != "emilkowalski/skills" or len(ek.get("skills", [])) != 15:
        raise ValueError("HOLD: upstream Kowalski manifest identity")
    emil_row = next(r for r in records if r["repo"] == "emilkowalski/skills")
    if emil_row["source_commit"] != ek["upstream"]["commit"]:
        raise ValueError("HOLD: inconsistent upstream pin")
    return {
        "status": "SOURCE_REGISTRY_VALIDATED_NOT_HOST_INSTALLED",
        "repositories": len(records),
        "historically_pinned": sum(bool(r["source_commit"]) for r in records),
        "pin_revalidation_required": sum(not bool(r["source_commit"]) for r in records),
        "license_holds": sorted(r["repo"] for r in records if r["license_gate"] in BLOCKED_LICENSE),
        "emil_skill_refs": len(ek["skills"]),
        "first_party_explicit_skill_files": reg["counts"]["first_party_explicit_skill_files_in_review_tree"],
        "first_party_generated_skill_definitions": reg["counts"]["first_party_generated_catalog_definitions"],
        "host_installation": "NOT_EVIDENCED",
        "human_release": "HOLD",
    }


def select(intent: str, limit: int = 12) -> dict:
    if intent not in INTENTS:
        raise ValueError("HOLD: unsupported intent")
    if not 1 <= limit <= 30:
        raise ValueError("HOLD: invalid result bound")
    audit()
    records = load(REGISTRY)["repositories"]
    chosen, deferred = [], []
    for r in records:
        tags = sorted(INTENTS[intent].intersection(r["capabilities"]))
        if not tags:
            continue
        reason = []
        if r["license_gate"] in BLOCKED_LICENSE:
            reason.append("LICENSE_OR_SUBPATH_REVIEW_REQUIRED")
        if r["disposition"] in BLOCKED_DISTRIBUTION:
            reason.append("REDISTRIBUTION_PROHIBITED_IN_FDF")
        if not r["source_commit"]:
            reason.append("EXACT_UPSTREAM_PIN_REVALIDATION_REQUIRED")
        item = {
            "repo": r["repo"], "capability_overlap": tags,
            "disposition": r["disposition"], "source_commit": r["source_commit"],
            "license_gate": r["license_gate"], "state": "REFERENCE_ONLY_UNTIL_APPROVED",
            "next_gate": reason or ["OWNER_DECISION_AND_HOST_POLICY_DISCOVERY"],
        }
        (deferred if r["license_gate"] in BLOCKED_LICENSE or r["disposition"] in BLOCKED_DISTRIBUTION else chosen).append(item)
    chosen.sort(key=lambda r: (-len(r["capability_overlap"]), r["source_commit"] is None, r["repo"]))
    deferred.sort(key=lambda r: r["repo"])
    return {
        "schema": "fdf.portfolio.fit_result/1.0",
        "intent": intent, "classification": "REFERENCE_RECOMMENDATION_ONLY",
        "source_basis": "HISTORIC_CANONICAL_AUDIT_NO_LIVE_UPSTREAM_FETCH",
        "recommended_references": chosen[:limit],
        "deferred": deferred,
        "first_party_route": ["fdf-project-observer", "fdf-governance-gate", "fdf-evolution-planner", "fdf-verification-engine"],
        "prohibited_effects": ["INSTALL", "ROOT_POLICY_EDIT", "NETWORK_EXECUTION", "GIT_PUSH", "DEPLOY"],
        "owner_ide_activation": "UNKNOWN_NOT_OBSERVED", "release": "HOLD",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "fit"))
    parser.add_argument("--intent", choices=sorted(INTENTS))
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args(argv)
    try:
        if args.command == "fit" and not args.intent:
            raise ValueError("HOLD: --intent required")
        result = audit() if args.command == "audit" else select(args.intent, args.limit)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
