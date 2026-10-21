#!/usr/bin/env python3
"""UAC-007: cooperative-workspace, additive-only Fabric installation transaction.

No existing root-policy changes, external installs, owner identity or IDE admission.
Native Windows tests and adversarial concurrent filesystem guarantees remain OPEN.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path
import fdf_adopt as prior

SCHEMA = 'fdf.uac007.transaction/0.1'
JOURNAL = '.fabrica/UAC007_TRANSACTION.json'
MANIFEST = prior.MANIFEST
MAX_ITEMS = 120


def sha(b): return hashlib.sha256(b).hexdigest()
def encoded(obj): return (json.dumps(obj, sort_keys=True, indent=2)+'\n').encode('utf-8')

def path(root, rel):
    p = prior.safe_path(root, rel)
    if len(rel.split('/')) > 12: raise ValueError('HOLD: excessive path nesting')
    return p

def regular_data(p):
    if p.is_symlink(): raise ValueError('HOLD: symlinked path')
    if not p.exists(): return None
    s = p.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_size > 1024*1024:
        raise ValueError('HOLD: nonregular or oversized installation file')
    with p.open('rb') as f: b = f.read(1024*1024+1)
    if len(b) > 1024*1024: raise ValueError('HOLD: oversized file')
    return b

def directory(root, relative):
    current = root
    for part in relative.split('/')[:-1]:
        current = current / part
        if current.is_symlink():raise ValueError('HOLD: linked parent')
        if current.exists():
            if not current.is_dir():raise ValueError('HOLD: parent not directory')
        else:
            current.mkdir()  # cooperative single-writer contract; no adversarial NT guarantee
        if current.is_symlink():raise ValueError('HOLD: linked parent changed')


def exclusive_file(root, rel, data):
    p = path(root, rel)
    directory(root, rel)
    p = path(root, rel)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(p, flags, 0o600)
    try:
        with os.fdopen(fd, 'wb', closefd=False) as f:
            f.write(data)
            f.flush()
            os.fsync(fd)
    finally:os.close(fd)
    return sha(data)


def clean_dirs(root, new_dirs):
    # Never remove a pre-existing caller directory, even if empty.
    dirs = [path(root, rel) for rel in new_dirs]
    for d in sorted(dirs,key=lambda x:len(x.parts),reverse=True):
        if d.is_symlink():raise ValueError('HOLD: cleanup encountered a symlink')
        try:d.rmdir()  # only empty directories
        except OSError:pass


def planned(root, platforms):
    plan, files = prior.generate_plan(root, platforms, 'none')
    if plan['collisions']:raise ValueError('HOLD: existing managed path collision')
    if path(root,JOURNAL).exists() or path(root, MANIFEST).exists():
        raise ValueError('HOLD: existing transaction or installation; use status/recover')
    selected=[]
    for a in plan['actions']:
        if a['kind'] != 'managed_new':raise ValueError('HOLD: existing-root modification forbidden')
        if a['status']=='ADD':
            b=files[a['path']].encode('utf-8')
            selected.append({'path':a['path'], 'sha256':sha(b), 'bytes':len(b)})
        elif a['status']!='ALREADY_PRESENT':raise ValueError('HOLD: unknown action')
    if len(selected)>MAX_ITEMS:raise ValueError('HOLD: too many files')
    # Existing matching paths stay caller-owned, and are never deleted.
    new_dirs = set()
    for rel in [a['path'] for a in selected] + [MANIFEST, JOURNAL]:
        parent = path(root, rel).parent
        while parent != root and root in parent.parents:
            if parent.is_symlink():raise ValueError('HOLD: symlink parent')
            if not parent.exists():new_dirs.add(parent.relative_to(root).as_posix())
            parent=parent.parent
    new_dirs = sorted(new_dirs)
    digest=sha(encoded({'root_fingerprint':plan['project_root_fingerprint'], 'platforms':plan['platforms'],
                       'files':selected, 'new_dirs':new_dirs, 'projectdna':plan['projectdna']}))
    return {'schema':SCHEMA, 'status':'REVIEW_ONLY', 'transaction_sha256':digest,
            'platforms':plan['platforms'], 'files':selected, 'new_dirs':new_dirs,
            'existing_root_policy_files_modified':False, 'owner_identity_verified':False,
            'windows_native_tested':False, 'actual_ide_verified':False,
            'filesystem_guarantee':'COOPERATIVE_SINGLE_WRITER_ONLY', 'release':'HOLD'}, files


def read_journal(root):
    data=regular_data(path(root,JOURNAL))
    if data is None:raise ValueError('HOLD: no transaction journal')
    j=json.loads(data)
    if j.get('schema') != SCHEMA or not isinstance(j.get('files'),list) or len(j['files'])>MAX_ITEMS:
        raise ValueError('HOLD: unsupported journal')
    if not isinstance(j.get('new_dirs'),list) or len(j['new_dirs'])>MAX_ITEMS:raise ValueError('HOLD: malformed directory journal')
    for rel in j['new_dirs']:
        if not isinstance(rel,str):raise ValueError('HOLD: malformed journal directory')
        path(root,rel)
    for a in j['files']:
        if (set(a)!={'path','sha256','bytes'} or not isinstance(a['path'],str) or
            not isinstance(a['sha256'],str) or len(a['sha256'])!=64 or
            not isinstance(a['bytes'],int) or a['bytes']<0 or a['bytes']>1024*1024):
            raise ValueError('HOLD: malformed journal item')
        path(root,a['path'])
    return j


def install(root, platforms, approval, *, trusted_single_writer=False, fault_after=None):
    if not trusted_single_writer:raise ValueError('HOLD: --trusted-single-writer required')
    plan, files=planned(root,platforms)
    if approval != plan['transaction_sha256']:raise ValueError('HOLD: stale plan approval digest')
    j={**plan,'status':'PREPARED'}
    # Journal must be on disk before any managed application file.
    exclusive_file(root,JOURNAL,encoded(j))
    for i,a in enumerate(j['files']):
        if regular_data(path(root,a['path'])) is not None:raise ValueError('HOLD: file appeared after plan')
        exclusive_file(root,a['path'], files[a['path']].encode('utf-8'))
        if fault_after is not None and i+1>=fault_after:raise RuntimeError('INJECTED_CRASH_BEFORE_MANIFEST')
    record={'schema':SCHEMA,'plan_sha256':approval,'paths':j['files'], 'release':'HOLD'}
    exclusive_file(root,MANIFEST,encoded(record))
    return {'status':'FILES_INSTALLED_ADVISORY_ONLY','count':len(j['files']), 'release':'HOLD',
            'actual_ide_verified':False,'windows_native_tested':False}


def status(root):
    j=read_journal(root)
    rows=[]
    for a in j['files']:
        data=regular_data(path(root,a['path']))
        rows.append({'path':a['path'], 'state':'ABSENT' if data is None else 'MATCH' if len(data)==a['bytes'] and sha(data)==a['sha256'] else 'DRIFT_HOLD'})
    m=regular_data(path(root,MANIFEST))
    manifest='ABSENT' if m is None else 'MATCH' if json.loads(m).get('plan_sha256')==j['transaction_sha256'] else 'DRIFT_HOLD'
    verdict='HOLD_DRIFT' if manifest=='DRIFT_HOLD' or any(x['state']=='DRIFT_HOLD' for x in rows) else 'COMPLETE_HASHES_MATCH' if manifest=='MATCH' and all(x['state']=='MATCH' for x in rows) else 'INTERRUPTED_RECOVERABLE'
    return {'schema':SCHEMA, 'verdict':verdict,'files':rows,'manifest':manifest,'release':'HOLD','actual_ide_verified':False}


def rollback(root,approval,*,trusted_single_writer=False):
    if not trusted_single_writer:raise ValueError('HOLD: --trusted-single-writer required')
    j=read_journal(root)
    if j['transaction_sha256']!=approval:raise ValueError('HOLD: transaction digest mismatch')
    current=status(root)
    if current['verdict']=='HOLD_DRIFT':raise ValueError('HOLD: owner drift; no deletion')
    # All preconditions checked before any delete; cooperative single-writer required.
    for a in reversed(j['files']):
        p=path(root,a['path'])
        if p.exists():p.unlink()
    m=path(root,MANIFEST)
    if m.exists():m.unlink()
    path(root,JOURNAL).unlink()
    clean_dirs(root,j['new_dirs'])
    return {'status':'MATCHED_MANAGED_FILES_REMOVED','root_policy_files_modified':False,
            'release':'HOLD'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['plan','apply','status','rollback'])
    parser.add_argument('--project',required=True)
    parser.add_argument('--platforms',default='codex,cursor,antigravity,gemini')
    parser.add_argument('--approve-plan')
    parser.add_argument('--root-hooks',default='none')
    parser.add_argument('--trusted-single-writer',action='store_true')
    args=parser.parse_args()
    try:
        root=prior.require_root(args.project)
        if args.root_hooks!='none':raise ValueError('HOLD: UAC007 forbids modifying existing root policies')
        platforms=[p.strip() for p in args.platforms.split(',') if p.strip()]
        if len(platforms)!=len(set(platforms)) or not platforms:raise ValueError('HOLD: invalid platforms')
        if args.command=='plan':out=planned(root,platforms)[0]
        elif args.command=='apply':out=install(root,platforms,args.approve_plan,trusted_single_writer=args.trusted_single_writer)
        elif args.command=='status':out=status(root)
        else:out=rollback(root,args.approve_plan,trusted_single_writer=args.trusted_single_writer)
        print(json.dumps(out,indent=2,sort_keys=True))
    except (OSError,ValueError,RuntimeError,json.JSONDecodeError) as e:
        print('HOLD: '+str(e),file=sys.stderr);return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
