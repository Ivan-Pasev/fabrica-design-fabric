#!/usr/bin/env python3
"""R42 host-operator intent gate: advisory only, with no mutation capability.

Evaluates a declarative snapshot. It cannot read/enforce private host policies,
verify genuine user approval, authenticate Git SHAs or invoke the host's agents.
"""
import argparse
import json
import re
from pathlib import PurePosixPath

PROPOSAL_REQUIRED = "HOLD_NO_CURRENT_ACCEPTED_PROPOSAL"
KNOWN = {"STATUS", "NEXT", "CONTINUE", "REVIEW", "REFINE", "CHECK", "PUBLISH", "DEPLOY"}
READ_ONLY = {"STATUS", "NEXT", "REVIEW", "REFINE", "CHECK"}


def evaluate(intent):
    if not isinstance(intent, dict) or set(intent) != {"operator", "host_sha", "pending", "accepted_proposal_id"}:
        raise ValueError("Invalid bounded operator intent schema")
    op = intent["operator"]
    if not isinstance(op, str):
        raise ValueError("Invalid operator type")
    # NEXT(UI), NEXT(UX), CHECK(ALL) are still read-only when qualified.
    match = re.fullmatch(r"([A-Z]+)(?:\(([A-Za-z0-9_+@:\-]*)\))?", op)
    normalized = match.group(1) if match else None
    base = {
        "schema": "fdf.host.operator-advice/0.1",
        "operator": op,
        "normalized_operator": normalized,
        "mode": "ADVISORY_ONLY",
        "host_mutation_executed": False,
        "host_mutation_authorized": False,
        "release": "HOLD",
        "claims": "DECLARED_INPUTS_NOT_AUTHENTICATED",
    }
    if normalized not in KNOWN:
        return dict(base, verdict="HOLD_UNKNOWN_OPERATOR")
    if normalized in READ_ONLY:
        return dict(base, verdict="HOST_READ_ONLY_OPERATOR", next_action="FOLLOW_HOST_LAW_NO_EDITS")
    if normalized in {"PUBLISH", "DEPLOY"}:
        return dict(base, verdict="HOLD_SEPARATE_HOST_RELEASE_OR_DEPLOY_OPERATOR",
                    next_action="REQUIRE_HOST_SPECIFIC_HUMAN_AUTHORITY")
    pending = intent["pending"]
    selected = intent["accepted_proposal_id"]
    host_sha = intent["host_sha"]
    if not isinstance(pending, dict) or set(pending) != {"id", "host_sha", "scope"}:
        return dict(base, verdict=PROPOSAL_REQUIRED)
    if not isinstance(selected, str) or not selected:
        return dict(base, verdict=PROPOSAL_REQUIRED)
    if (not isinstance(pending["id"], str) or pending["id"] != selected or
            not isinstance(host_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", host_sha) or
            pending["host_sha"] != host_sha):
        return dict(base, verdict="HOLD_STALE_OR_UNACCEPTED_PROPOSAL")
    scope = pending["scope"]
    if not isinstance(scope, list) or not 1 <= len(scope) <= 12:
        return dict(base, verdict="HOLD_SCOPE_UNKNOWN_OR_EXCESSIVE")
    for path in scope:
        if not isinstance(path, str) or not path or len(path) > 240 or "\\" in path:
            return dict(base, verdict="HOLD_INVALID_PROPOSAL_PATH")
        parts = PurePosixPath(path).parts
        if (PurePosixPath(path).is_absolute() or any(part in (".", "..", "") for part in parts)
            or path.startswith("~") or "\x00" in path):
            return dict(base, verdict="HOLD_INVALID_PROPOSAL_PATH")
    if len(set(scope)) != len(scope):
        return dict(base, verdict="HOLD_DUPLICATE_SCOPE")
    # Advisory scope admission is not a grant, and is intentionally narrower
    # than all project files an owner's actual IDE may legitimately change.
    ui_ext = {".css", ".scss", ".sass", ".less", ".html", ".jsx", ".tsx",
              ".vue", ".svelte", ".astro"}
    science_ext = {".md", ".mdx", ".markdown", ".tex", ".bib"}
    governed = {"agents.md", "claude.md", "gemini.md", "ai_critical.md",
                "package.json", "package-lock.json", "pnpm-lock.yaml",
                "yarn.lock", "tsconfig.json", "jsconfig.json", ".cursorrules",
                "vite.config.ts", "next.config.mjs", "astro.config.mjs"}
    protected = {".git", ".github", ".agents", ".cursor", ".vscode", ".idea",
                 "node_modules", "vendor", "dist", "build", "coverage",
                 "private", "secrets", "ver", "release", "releases"}
    for name in scope:
        parts = name.split("/")
        lowered = [part.lower() for part in parts]
        if (any(part in ("", ".", "..") for part in parts) or
                ":" in name or "%" in name or "//" in name):
            return dict(base, verdict="HOLD_INVALID_PROPOSAL_PATH")
        if (lowered[-1].startswith(".env") or lowered[-1] in governed or
                any(part in protected for part in lowered[:-1])):
            return dict(base, verdict="HOLD_PROTECTED_PROPOSAL_PATH")
        hidden = [i for i, part in enumerate(lowered[:-1]) if part.startswith(".")]
        if hidden and not (hidden == [0] and lowered[:2] == [".vitepress", "theme"]):
            return dict(base, verdict="HOLD_PROTECTED_PROPOSAL_PATH")
        suffix = PurePosixPath(name).suffix.lower()
        if suffix in science_ext:
            return dict(base, verdict="HOLD_CONTENT_OR_SCIENCE_REVIEW_REQUIRED")
        if suffix not in ui_ext:
            return dict(base, verdict="HOLD_OUTSIDE_UI_ONLY_SCOPE")
    # This is never a grant. A host IDE must reconcile live HEAD, dirty state,
    # applicable nested/global policies, explicit permission and actual source.
    return dict(base, verdict="HOST_CONTINUE_PREFLIGHT_ONLY",
                next_action="HOST_MASTER_REVALIDATE_AND_ENFORCE_OWN_AUTHORIZATION")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intent", help="Path to caller-provided JSON intent; omit to read stdin")
    args = parser.parse_args()
    try:
        if args.intent:
            from pathlib import Path
            path = Path(args.intent)
            if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
                raise ValueError("Unreadable or oversized intent file")
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            import sys
            raw = sys.stdin.read(65537)
            if len(raw) > 65536:
                raise ValueError("Oversized operator intent")
            data = json.loads(raw)
        print(json.dumps(evaluate(data), indent=2, sort_keys=True))
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(2, "HOLD: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
