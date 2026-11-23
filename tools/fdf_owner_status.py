#!/usr/bin/env python3
"""UAC-014: privacy-minimized, read-only owner project status for FDF().

This is NOT native host skill discovery, activation, approval or installation.
This status probe DOES NOT READ POLICY CONTENTS, CALL GIT, OR COMPUTE HASHES.
The separate UAC-010 ProjectDNA witness remains available for a privately
approved evidence collection. No files are intentionally written and no
external requests are made.
"""
from __future__ import annotations
import argparse
import os
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
MAX_VISITED_DIRECTORIES = 256
MAX_VISITED_ENTRIES = 4000
MAX_POLICY_ITEMS = 60
MAX_DEPTH = 4


def metadata_only_capture(project: str, host: str, intent: str) -> dict:
    """Bounded path metadata scan. No open/read_bytes, Git or external source use."""
    if host not in fdf_projectdna.HOSTS:
        raise ValueError("HOLD: unrecognized self-declared host")
    if intent not in fdf_projectdna.fdf_portfolio.INTENTS:
        raise ValueError("HOLD: unsupported intent")

    supplied = Path(project).expanduser()
    if is_link_or_junction(supplied):
        raise ValueError("HOLD: linked project root")
    root = supplied.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("HOLD: project root not a directory")

    policy_rows = []
    unsafe_paths = []
    incomplete = False
    stack = [(root, 0)]
    total_entries = 0
    total_dirs = 0
    allowed_policies = fdf_projectdna.POLICY_NAMES
    adapters = fdf_projectdna.ADAPTER_DIRS
    ignored = fdf_projectdna.IGNORE_DIRS

    while stack:
        directory, depth = stack.pop()
        total_dirs += 1
        if total_dirs > MAX_VISITED_DIRECTORIES:
            incomplete = True
            break
        try:
            with os.scandir(directory) as scan:
                for entry in scan:
                    total_entries += 1
                    if total_entries > MAX_VISITED_ENTRIES:
                        incomplete = True
                        break
                    name = entry.name
                    entry_path = Path(entry.path)
                    relative = entry_path.relative_to(root).as_posix()
                    if is_link_or_junction(entry_path):
                        if name in allowed_policies or name in (".agents", ".cursor", ".gemini", ".claude"):
                            unsafe_paths.append("SYMLINK_OR_JUNCTION_HOLD")
                        continue
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            if name not in ignored and depth < MAX_DEPTH:
                                stack.append((entry_path, depth + 1))
                        elif entry.is_file(follow_symlinks=False):
                            is_policy = name in allowed_policies or relative == ".github/copilot-instructions.md"
                            is_adapter = any(relative.startswith(x + "/") and
                                             name.endswith((".md", ".mdc")) for x in adapters)
                            if is_policy or is_adapter:
                                if len(policy_rows) >= MAX_POLICY_ITEMS:
                                    incomplete = True
                                    break
                                policy_rows.append({"state": "PRESENT_METADATA_ONLY"})
                    except OSError:
                        incomplete = True
                if incomplete:
                    break
        except OSError:
            incomplete = True

    signals, holds = fdf_projectdna.workspace_signals(root)
    for rel in adapters:
        if is_link_or_junction(root / rel):
            unsafe_paths.append("LINKED_ADAPTER_HOLD")
    unsafe_paths.extend(holds)
    return {
        "host_self_declared": host,
        "observed_policy_files": policy_rows,
        "policy_inventory_truncated": incomplete,
        "unsafe_adapter_paths": unsafe_paths,
        "framework_signals": signals,
        "git": {"git_status": "UNKNOWN"},
        "audit_status": ("HOLD_INCOMPLETE_OR_UNSAFE_OBSERVATION"
                         if incomplete or unsafe_paths else "LOCAL_METADATA_ONLY"),
    }


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
        "git_subprocess_invoked": False,
        "policy_file_contents_accessed": False,
        "policy_file_hashes_computed": False,
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
    observed = metadata_only_capture(project, host, intent)
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
        # Exceptions may contain private absolute paths: never echo exception text.
        if isinstance(error, FileNotFoundError):
            label = "CALLER_WORKSPACE_NOT_ACCESSIBLE"
        elif isinstance(error, PermissionError):
            label = "CALLER_WORKSPACE_PERMISSION_DENIED"
        elif isinstance(error, ValueError):
            label = "INVALID_INPUT_OR_UNSAFE_WORKSPACE"
        else:
            label = "LOCAL_STATUS_PROBE_FAILED"
        print("HOLD: " + label, file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
