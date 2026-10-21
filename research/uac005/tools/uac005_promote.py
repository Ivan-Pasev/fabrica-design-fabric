#!/usr/bin/env python3
"""UAC-005: stage an exact pinned ZIP in a CLEAN existing Git checkout.

Not an installer, release, signer, or automatic Git commit/push tool.
Requires operator-reviewed exact plan SHA for any repository writes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile
import zipfile

PIN = "de833726ce83117d0305cad1af04c4fc88578bd031eb439377ff46968c70ccdf"
DEST = Path("distribution/uac-v0.2")
MAX_TOTAL = 512_000
MAX_FILES = 20


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def git_root(root: str | Path) -> Path:
    root = Path(root).absolute()
    if not root.is_dir() or root.is_symlink():
        raise ValueError("HOLD: checkout directory invalid or symlinked")
    p = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if p.returncode or Path(p.stdout.strip()).resolve() != root.resolve():
        raise ValueError("HOLD: expected actual Git checkout root")
    dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"], capture_output=True, text=True)
    if dirty.returncode or dirty.stdout.strip():
        raise ValueError("HOLD: checkout has existing changes")
    return root


def verified_archive(archive: str | Path) -> tuple[dict, dict[str, bytes]]:
    archive = Path(archive)
    if not archive.is_file() or digest(archive.read_bytes()) != PIN:
        raise ValueError("HOLD: pinned ZIP SHA mismatch")
    with zipfile.ZipFile(archive) as z:
        info = z.infolist()
        if len(info) > MAX_FILES or sum(m.file_size for m in info) > MAX_TOTAL:
            raise ValueError("HOLD: ZIP size or count threshold exceeded")
        names = [x.filename for x in info]
        if len(set(names)) != len(names) or "FABRICA_MANIFEST.json" not in names:
            raise ValueError("HOLD: duplicate names or missing source manifest")
        for i in info:
            p = PurePosixPath(i.filename)
            if i.is_dir() or p.is_absolute() or ".." in p.parts or "\\" in i.filename or any(not s or s == "." for s in i.filename.split("/")):
                raise ValueError("HOLD: invalid ZIP entry path")
            if (i.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("HOLD: source ZIP symlink")
        manifest = json.loads(z.read("FABRICA_MANIFEST.json"))
        entries = manifest.get("files", [])
        if manifest.get("schema") != "fdf.source-manifest/0.2" or len(entries) != 14 or manifest.get("entry_count") != 14:
            raise ValueError("HOLD: unexpected manifest schema or count")
        files = {name: z.read(name) for name in names if name != "FABRICA_MANIFEST.json"}
        if set(files) != {e.get("path") for e in entries}:
            raise ValueError("HOLD: unmanifested ZIP file")
        for entry in entries:
            body = files[entry["path"]]
            if len(body) != entry["bytes"] or digest(body) != entry["sha256"]:
                raise ValueError("HOLD: source manifest digest mismatch")
        return manifest, files


def plan(archive: str, checkout: str) -> dict:
    root = git_root(checkout)
    manifest, files = verified_archive(archive)
    parent = root / DEST.parent
    dest = root / DEST
    if parent.is_symlink() or (parent.exists() and not parent.is_dir()) or dest.exists() or dest.is_symlink():
        raise ValueError("HOLD: existing output or unsafe distribution directory")
    details = {"schema": "fdf.uac005.source-import/0.1", "checkout": str(root), "archive_sha256": PIN,
               "destination": DEST.as_posix(), "files": [{"path": e["path"], "sha256": e["sha256"], "bytes": e["bytes"]} for e in manifest["files"]],
               "git_commit_created": False, "network_access": False, "caller_root_modified": False, "release": "HOLD"}
    details["plan_sha256"] = digest(canonical(details))
    return details


def apply(archive: str, checkout: str, approval: str) -> dict:
    current = plan(archive, checkout)
    if approval != current["plan_sha256"]:
        raise ValueError("HOLD: exact approval digest required")
    root = Path(checkout).absolute()
    parent = root / DEST.parent
    made_parent = not parent.exists()
    if made_parent:
        parent.mkdir(mode=0o700)
    temp = None
    try:
        temp = Path(tempfile.mkdtemp(prefix=".uac005_stage_", dir=parent))
        _, files = verified_archive(archive)
        for rel, body in files.items():
            target = temp / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as f:
                f.write(body)
        (temp / "FABRICA_MANIFEST.json").write_text(json.dumps(json.loads(zipfile.ZipFile(archive).read("FABRICA_MANIFEST.json")), sort_keys=True, indent=2) + "\n")
        for entry in current["files"]:
            if digest((temp / entry["path"]).read_bytes()) != entry["sha256"]:
                raise ValueError("HOLD: temporary source drift")
        if (root / DEST).exists():
            raise ValueError("HOLD: output appeared during staging")
        temp.rename(root / DEST)
        temp = None
    finally:
        if temp is not None:
            shutil.rmtree(temp)
            if made_parent and parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
    return {"status": "STAGED_IN_GIT_WORKTREE_NOT_COMMITTED", "destination": DEST.as_posix(),
            "files_imported": len(current["files"]), "git_commit_created": False, "release": "HOLD"}


def verify(checkout: str) -> dict:
    root = Path(checkout).absolute()
    path = root / DEST
    if not path.is_dir() or path.is_symlink():
        raise ValueError("HOLD: staged subtree missing")
    manifest = json.loads((path / "FABRICA_MANIFEST.json").read_text())
    if manifest.get("entry_count") != 14:
        raise ValueError("HOLD: staged manifest invalid")
    entries = manifest["files"]
    expected = {e["path"] for e in entries} | {"FABRICA_MANIFEST.json"}
    actual = {p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file()}
    if actual != expected or any(p.is_symlink() for p in path.rglob("*")):
        raise ValueError("HOLD: staged files changed")
    for entry in entries:
        data = (path / entry["path"]).read_bytes()
        if len(data) != entry["bytes"] or digest(data) != entry["sha256"]:
            raise ValueError("HOLD: staged SHA drift")
    return {"status": "SOURCE_PARITY_LOCAL_WORKTREE_ONLY", "source_files_verified": 14, "release": "HOLD"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("plan", "apply", "verify"))
    p.add_argument("--archive")
    p.add_argument("--checkout", required=True)
    p.add_argument("--approve-plan")
    args = p.parse_args()
    try:
        if args.command == "verify": result = verify(args.checkout)
        elif not args.archive: raise ValueError("HOLD: --archive required")
        elif args.command == "plan": result = plan(args.archive, args.checkout)
        elif not args.approve_plan: raise ValueError("HOLD: --approve-plan required")
        else: result = apply(args.archive, args.checkout, args.approve_plan)
        print(json.dumps(result, sort_keys=True, indent=2))
    except (OSError, ValueError, zipfile.BadZipFile, KeyError, TypeError) as e:
        p.exit(2, str(e) + "\n")

if __name__ == "__main__":
    main()
