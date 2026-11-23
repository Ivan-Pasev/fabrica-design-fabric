#!/usr/bin/env python3
"""UAC-014: privacy-minimized, read-only owner project status for FDF().

This is NOT native host skill discovery, activation, approval or installation.
The underlying ProjectDNA witness reads bounded policy files to hash them; raw
content, paths, policy hashes, Git SHA and project basename are OMITTED here.
No files are intentionally written and no external requests are made.
"""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import re
import sys
import json

import fdf_projectdna

SKILL_DIRECTORIES = (
    ".agents/skills", ".gemini/skills", ".cursor/skills", ".claude/skills"
)
SKILL_PATTERN = re.compile(r"^fdf-[a-z0-9-]{1,64}$")
MAX_CANDIDATES = 40


def is_link_or_junction(path: Path) -> bool:
    try:
        return path.is_symlink() or bool(getattr(path, "is_junction", lambda: False)())
    except OSError:
        return True


def inspect_on_disk_candidates(root: Path) -> dict:
    """Only look for FDF-named SKILL.md files; never read their contents."""
    found: set[str] = set()
    unsafe = False
    scan_incomplete = False
    for relative in SKILL_DIRECTORIES:
        parent = root
        for component in relative.split("/"):
            parent = parent / component
            if is_link_or_junction(parent):
                unsafe = True
                break
            if not parent.exists():
                parent = None
                break
            if not parent.is_dir():
                unsafe = True
                break
        if parent is None or unsafe:
            continue
        try:
            children = sorted(parent.iterdir(), key=lambda item: item.name)
            if len(children) > MAX_CANDIDATES:
                scan_incomplete = True
                children = children[:MAX_CANDIDATES]
            for candidate in children:
                if not SKILL_PATTERN.fullmatch(candidate.name):
                    continue
                if is_link_or_junction(candidate) or not candidate.is_dir():
                    unsafe = True
                    continue
                file = candidate / "SKILL.md"
                if is_link_or_junction(file):
                    unsafe = True
                    continue
                if file.is_file():
                    found.add(candidate.name)
        except OSError:
            scan_incomplete = True
    return {
        "fdf_skill_file_candidates_on_disk": sorted(found),
        "source_identity_of_local_skill_files_verified": False,
        "native_host_skill_discovery_verified": False,
        "native_host_skill_activation_verified": False,
        "unsafe_skill_paths_detected": unsafe,
        "scan_incomplete": scan_incomplete,
        "source_file_presence_is_not_host_activation": True,
    }


def summarize(witness: dict, file_candidates: dict) -> dict:
    """Explicit allowlist projection: never serialize the original witness."""
    rows = witness.get("observed_policy_files", [])
    if not isinstance(rows, list):
        raise ValueError("HOLD: invalid ProjectDNA policy inventory")
    for item in rows:
        if not isinstance(item, dict) or not isinstance(item.get("state"), str):
            raise ValueError("HOLD: malformed ProjectDNA policy entry")
    observed_states = dict(sorted(Counter(row["state"] for row in rows).items()))
    allowed_states = {"CLEAN", "CHANGES_OR_UNTRACKED", "UNKNOWN"}
    git_status = witness.get("git", {}).get("git_status", "UNKNOWN")
    if git_status not in allowed_states:
        git_status = "UNKNOWN"
    unsafe = bool(witness.get("unsafe_adapter_paths")) or file_candidates["unsafe_skill_paths_detected"]
    truncated = bool(witness.get("policy_inventory_truncated")) or file_candidates["scan_incomplete"]
    supported_signals = set((
        "nextjs", "node", "python", "rust", "go", "java", "flutter", "dotnet",
        "web-static",
    ))
    signals = witness.get("framework_signals", [])
    if not isinstance(signals, list):
        raise ValueError("HOLD: malformed framework markers")
    result = {
        "schema": "fdf.owner_pilot.minimal_status/0.1",
        "classification": "LOCAL_METADATA_OBSERVATION_NOT_IDE_ACTIVATION",
        "declared_host": witness.get("host_self_declared", "unknown"),
        "declared_host_not_authenticated": True,
        "framework_marker_types": sorted(set(x for x in signals if isinstance(x, str) and x in supported_signals)),
        "bounded_policy_file_count": len(rows),
        "bounded_policy_state_counts": observed_states,
        "global_and_effective_host_rules": "UNKNOWN_NOT_INSPECTED",
        "git_state": git_status,
        "git_commit_sha_disclosed": False,
        "project_name_and_absolute_path_disclosed": False,
        "policy_paths_content_and_hashes_disclosed": False,
        "on_disk": file_candidates,
        "read_only_intended": True,
        "independent_human_witness_present": False,
        "owner_approval_verified": False,
        "permissions_to_install_or_modify": False,
        "permission_to_merge_or_release": False,
        "next_owner_step": (
            "Inspect actual IDE skill UI/list and effective rules; if FDF not discovered, "
            "STOP before installation. Use original UAC-010 witness privately for evidence intake."
        ),
        "release": "HOLD",
    }
    result["status"] = ("HOLD_UNSAFE_OR_INCOMPLETE_FILESYSTEM_INVENTORY"
                        if unsafe or truncated or witness.get("audit_status") != "LOCAL_METADATA_ONLY"
                        else "PRIVACY_MINIMIZED_READ_ONLY_METADATA")
    return result


def status(project: str, host: str, intent: str) -> dict:
    observed = fdf_projectdna.capture(project, host, intent)
    path = Path(project).expanduser().resolve(strict=True)
    return summarize(observed, inspect_on_disk_candidates(path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["status"])
    parser.add_argument("--project", required=True)
    parser.add_argument("--host", choices=fdf_projectdna.HOSTS, default="unknown")
    parser.add_argument("--intent", choices=[
        "design", "motion", "spatial", "quality", "mobile",
        "tokens", "runtime", "components"
    ], default="design")
    args = parser.parse_args(argv)
    try:
        report = status(args.project, args.host, args.intent)
    except (OSError, ValueError, RuntimeError, TypeError) as error:
        print("HOLD: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
