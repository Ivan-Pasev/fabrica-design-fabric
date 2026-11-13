#!/usr/bin/env python3
"""Read-only verifier of a complete pinned Git worktree, for independent CI evidence.

Source proof scope: exact tracked blobs at commit, count, on-disk contents.
It does not execute tests or certify upstream functionality.
"""
import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys


def call(root, *argv):
    return subprocess.check_output(['git', '-C', str(root), *argv], stderr=subprocess.PIPE)


def verify(root, expected_sha, expected_count):
    root = pathlib.Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('root must be a directory')
    head = call(root, 'rev-parse', 'HEAD').decode('ascii').strip()
    if head != expected_sha:
        raise ValueError(f'wrong commit: {head} != {expected_sha}')
    raw = call(root, 'ls-tree', '-r', '-z', 'HEAD')
    entries = []
    for record in raw.split(b'\0'):
        if not record:
            continue
        if b'\t' not in record:
            raise ValueError('malformed git tree record')
        meta, path_bytes = record.split(b'\t', 1)
        mode, typ, blob = meta.decode('ascii').split(' ')
        path = path_bytes.decode('utf-8')
        p = pathlib.PurePosixPath(path)
        if typ != 'blob' or mode not in ('100644', '100755'):
            raise ValueError(f'unsupported git object/mode: {path} {typ} {mode}')
        if p.is_absolute() or '..' in p.parts or not path:
            raise ValueError(f'unsafe path {path}')
        source = root.joinpath(*p.parts)
        if source.is_symlink() or not source.is_file():
            raise ValueError(f'non-file / symlink {path}')
        data = source.read_bytes()
        githash = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
        if githash != blob:
            raise ValueError(f'blob content mismatch: {path}')
        entries.append({'path': path, 'git_blob_sha1': blob, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'mode': mode})
    if len(entries) != expected_count:
        raise ValueError(f'incomplete tracked tree: {len(entries)} != {expected_count}')
    entries.sort(key=lambda r: r['path'].encode('utf-8'))
    canonical = ''.join(f'{e["path"]}\0{e["sha256"]}\n' for e in entries)
    root_sha256 = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    return {'format': 'fab.visual.anatomy.full-tree-evidence.v1', 'status': 'SOURCE_PARITY_PASS_NOT_UPSTREAM_TEST_CERTIFIED', 'source': 'https://github.com/wheresryan22/anatomy', 'commit': head, 'tracked_blobs': len(entries), 'root_sha256': root_sha256, 'files': entries, 'limitations': ['Git snapshot verifies only tracked bytes, not executable correctness', 'Examples include binary PDFs and images', 'Script did not attest any browser, geometry, accessibility or print correctness']}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True)
    p.add_argument('--commit', required=True)
    p.add_argument('--count', type=int, default=173)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    try:
        receipt = verify(a.root, a.commit, a.count)
        out = pathlib.Path(a.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(json.dumps({k: v for k, v in receipt.items() if k != 'files'}, sort_keys=True))
    except (OSError, ValueError, subprocess.CalledProcessError, UnicodeError) as exc:
        print(json.dumps({'status': 'SOURCE_PARITY_FAIL', 'reason': str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
