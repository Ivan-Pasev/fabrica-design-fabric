#!/usr/bin/env python3
"""Deterministic, source-only, fail-closed FAB.VISUAL alpha packer.
Archives exact working source tree into a canonical ZIP and file-hash manifest.
No live CodexStation installation, release approval or upstream completeness claim.
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, stat, sys, zipfile
OMIT_DIRS = {'.git', '.venv', '.pytest_cache', '__pycache__', 'node_modules', 'dist', 'evidence'}
OMIT_FILES = {'.DS_Store'}
REQUIRED = {'LICENSE', 'NOTICE', 'UPSTREAM_LOCK.json', 'vendor/anatomy/LICENSE',
            'scripts/install-codexstation.mjs', 'src/adapters/anatomy-kernel.mjs'}
def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()
def pack(root: pathlib.Path, out: pathlib.Path, commit: str) -> dict:
    root = root.resolve(strict=True)
    if not root.is_dir() or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('expected existing source root and full lowercase commit SHA')
    selected = []
    for path in sorted(root.rglob('*')):
        relpath = path.relative_to(root)
        if set(relpath.parts) & OMIT_DIRS or path.name in OMIT_FILES:
            continue
        if path.is_symlink():
            raise ValueError(f'symlink not admitted: {relpath}')
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f'unsupported file type: {relpath}')
        rel = relpath.as_posix()
        selected.append((rel, path.read_bytes()))
    present = {p for p, _ in selected}
    if REQUIRED - present:
        raise ValueError(f'missing required source files: {sorted(REQUIRED - present)}')
    members = [{'path': p, 'sha256': sha256(b), 'bytes': len(b)} for p,b in selected]
    root_hash = sha256(('\n'.join(f'{e["path"]} {e["sha256"]}' for e in members)+'\n').encode())
    manifest = {
        'schema': 'fab.visual.source-snapshot.v0.1', 'version': '0.3.0-alpha.0+omega8-candidate',
        'git_commit': commit, 'source_count': len(members), 'source_root_sha256': root_hash,
        'scope': 'first-party and pinned five-file Anatomy subset; NOT full upstream checkout',
        'release': 'HOLD', 'files': members,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path, data in selected:
            i = zipfile.ZipInfo('fab-visual/'+path, date_time=(1980,1,1,0,0,0))
            i.compress_type = zipfile.ZIP_DEFLATED
            i.external_attr = (stat.S_IFREG|0o644)<<16
            z.writestr(i, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        i = zipfile.ZipInfo('SOURCE_SNAPSHOT_MANIFEST.json', date_time=(1980,1,1,0,0,0))
        i.compress_type = zipfile.ZIP_DEFLATED
        i.external_attr = (stat.S_IFREG|0o644)<<16
        z.writestr(i,(json.dumps(manifest, sort_keys=True, indent=2)+'\n').encode())
    actual_sha = sha256(out.read_bytes())
    out.with_suffix(out.suffix+'.sha256').write_text(actual_sha+'  '+out.name+'\n')
    return {'zip': str(out), 'sha256': actual_sha, 'files': len(members), 'root_sha256':root_hash, 'commit':commit}
if __name__=='__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=str(pathlib.Path(__file__).resolve().parents[1]))
    ap.add_argument('--out',required=True)
    ap.add_argument('--commit',required=True)
    args=ap.parse_args()
    try:
        print(json.dumps(pack(pathlib.Path(args.root),pathlib.Path(args.out),args.commit), sort_keys=True))
    except (ValueError,OSError) as e:
        print('SOURCE_SNAPSHOT_HOLD: '+str(e),file=sys.stderr)
        sys.exit(2)
