#!/usr/bin/env python3
"""FDF/UAC-010 opt-in, read-only caller ProjectDNA witness.

A local metadata snapshot is not proof of host instruction precedence, owner
approval, skill activation, source trust, or filesystem safety. It does not
transmit, clone, install, create receipts on disk, or read policy prose into output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import fdf_portfolio

POLICY_NAMES = frozenset({"AGENTS.md", "GEMINI.md", "CLAUDE.md", "AI_CRITICAL.md", ".cursorrules", ".github/copilot-instructions.md"})
ADAPTER_DIRS = (".cursor/rules", ".agents/rules", ".agents/skills", ".gemini/skills", ".claude/skills")
IGNORE_DIRS = frozenset({".git", ".next", ".venv", "venv", "node_modules", "dist", "build", "coverage", ".turbo", ".cache", "__pycache__", ".fabrica"})
HOSTS = ("codex", "cursor", "antigravity", "gemini-cli", "ai-studio", "chatgpt-project", "unknown")
MAX_POLICIES = 60
MAX_POLICY_BYTES = 256_000

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical(obj: dict) -> bytes:
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")

def contained(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False

def policy_rows(root: Path) -> tuple[list[dict], bool]:
    """Metadata-only bounded inventory; refuses symlinked policy files."""
    rows: list[dict] = []
    truncated = False
    for where, dirs, files in os.walk(root, topdown=True, followlinks=False):
        directory = Path(where)
        rel_dir = directory.relative_to(root)
        depth = len(rel_dir.parts)
        dirs[:] = sorted(d for d in dirs if d not in IGNORE_DIRS and not (directory / d).is_symlink() and depth < 4)
        for name in sorted(files):
            p = directory / name
            relative = p.relative_to(root).as_posix()
            if name not in POLICY_NAMES and relative != ".github/copilot-instructions.md":
                if not (relative.startswith(ADAPTER_DIRS) and (name.endswith(".md") or name.endswith(".mdc"))):
                    continue
            if len(rows) >= MAX_POLICIES:
                truncated = True
                break
            if p.is_symlink():
                rows.append({"relative_path": relative, "state": "SYMLINK_HOLD"})
                continue
            try:
                stat = p.stat()
                if not p.is_file() or stat.st_size > MAX_POLICY_BYTES:
                    rows.append({"relative_path": relative, "state": "NONREGULAR_OR_LARGE_HOLD"})
                    continue
                data = p.read_bytes()
                if len(data) > MAX_POLICY_BYTES:
                    rows.append({"relative_path": relative, "state": "LARGE_HOLD"})
                    continue
                rows.append({"relative_path": relative, "state": "PRESENT_HASH_ONLY", "bytes": len(data), "sha256": digest(data)})
            except OSError:
                rows.append({"relative_path": relative, "state": "UNREADABLE_HOLD"})
        if truncated:
            break
    return rows, truncated

def workspace_signals(root: Path) -> tuple[list[str], list[str]]:
    markers = {
        "nextjs": ["next.config.js", "next.config.mjs", "next.config.ts"],
        "node": ["package.json"],
        "python": ["pyproject.toml", "requirements.txt", "setup.py"],
        "rust": ["Cargo.toml"],
        "go": ["go.mod"],
        "java": ["pom.xml", "build.gradle"],
        "flutter": ["pubspec.yaml"],
        "dotnet": ["*.sln", "*.csproj"],
        "web-static": ["index.html"],
    }
    present, holds = [], []
    for signal, patterns in markers.items():
        if any(any(root.glob(p)) for p in patterns):
            present.append(signal)
    for dir_name in ADAPTER_DIRS:
        p = root / dir_name
        if p.is_symlink():
            holds.append("ADAPTER_SYMLINK_HOLD:" + dir_name)
        elif p.is_dir():
            present.append("adapters:" + dir_name)
    return sorted(present), sorted(holds)

def git_witness(root: Path) -> dict:
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    args = ["git", "-C", str(root), "-c", "core.fsmonitor=false"]
    def run(extra: list[str]):
        try:
            c = subprocess.run(args + extra, text=True, capture_output=True, timeout=7, env=env, check=False)
            return c.stdout.strip() if c.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            return None
    toplevel = run(["rev-parse", "--show-toplevel"])
    head = run(["rev-parse", "--verify", "HEAD"])
    status = run(["status", "--porcelain", "--untracked-files=normal"]) if head else None
    in_scope = bool(toplevel and Path(toplevel).resolve() == root)
    return {
        "head_sha": head if in_scope and head and len(head) == 40 else None,
        "root_matches_git_toplevel": in_scope if toplevel else None,
        "git_status": "UNKNOWN" if status is None else "CLEAN" if not status else "CHANGES_OR_UNTRACKED",
        "gitignore_exclusions_not_exhaustively_observed": True,
    }

def capture(root_name: str, host: str, intent: str) -> dict:
    if host not in HOSTS:
        raise ValueError("HOLD: unrecognized self-declared host")
    root_input = Path(root_name).expanduser()
    if root_input.is_symlink():
        raise ValueError("HOLD: caller root is a symlink")
    root = root_input.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("HOLD: project is not a directory")
    policies, truncated = policy_rows(root)
    signals, holds = workspace_signals(root)
    fit = fdf_portfolio.select(intent, limit=12)
    git = git_witness(root)
    status = "HOLD_INCOMPLETE_OR_UNSAFE_OBSERVATION" if truncated or holds or any(r["state"] != "PRESENT_HASH_ONLY" for r in policies) else "LOCAL_METADATA_ONLY"
    witness = {
        "schema": "fdf.projectdna.local_witness/0.1",
        "project_name": root.name,
        "caller_path_disclosed": False,
        "host_self_declared": host,
        "host_executable_identity_verified": False,
        "framework_signals": signals,
        "observed_policy_files": policies,
        "policy_inventory_truncated": truncated,
        "unsafe_adapter_paths": holds,
        "git": git,
        "project_fit": fit,
        "source_registry_identity": "fdf.portfolio.third_party_sources/1.0.0",
        "local_host_global_policies": "UNKNOWN_NOT_INSPECTED",
        "effective_instruction_precedence": "UNKNOWN_NOT_WITNESSED",
        "skill_loading": "UNKNOWN_NOT_WITNESSED",
        "owner_approval": "NOT_OBSERVED",
        "filesystem_changes": "NONE_INTENDED",
        "audit_status": status,
        "release": "HOLD",
    }
    witness["witness_sha256"] = digest(canonical(witness))
    return witness

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["witness"])
    parser.add_argument("--project", required=True)
    parser.add_argument("--host", choices=HOSTS, default="unknown")
    parser.add_argument("--intent", choices=sorted(fdf_portfolio.INTENTS), default="design")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(capture(args.project, args.host, args.intent), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, RuntimeError) as err:
        print(str(err), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
