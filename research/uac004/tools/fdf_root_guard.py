#!/usr/bin/env python3
"""UAC-004 review-only POSIX root-hook guard; not wired into v0.2 installer.

No-follow directory-relative file handles, append-only root hook, digest and inode
verification, fsynced pre-mutation recovery journal. Not a privileged policy grant.
On Windows/unsupported file locking environments, fail closed.
"""
from __future__ import annotations
import hashlib
import json
import os
import stat
from pathlib import Path

MAX_FILE=1024*1024
FILE_NAMES=frozenset(("AGENTS.md","GEMINI.md"))


def sha(data): return hashlib.sha256(data).hexdigest()


def canonical(data): return (json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()


def require_platform():
    if os.name != "posix" or not hasattr(os,"O_NOFOLLOW") or not hasattr(os,"O_DIRECTORY"):
        raise ValueError("HOLD: POSIX no-follow root hook not supported on this host")
    import fcntl
    return fcntl


def root_fd(root):
    require_platform()
    path=Path(root).absolute()
    return os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)


def file_fd(rfd, name):
    if name not in FILE_NAMES: raise ValueError("HOLD: root hook target not allowlisted")
    fd=os.open(name,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=rfd)
    s=os.fstat(fd)
    if not stat.S_ISREG(s.st_mode) or s.st_size>MAX_FILE:
        os.close(fd);raise ValueError("HOLD: nonregular/oversized root hook")
    p=os.stat(name,dir_fd=rfd,follow_symlinks=False)
    if (s.st_dev,s.st_ino)!=(p.st_dev,p.st_ino):
        os.close(fd);raise ValueError("HOLD: root hook inode changed")
    return fd


def read_fd(fd):
    os.lseek(fd,0,os.SEEK_SET)
    data=os.read(fd,MAX_FILE+1)
    if len(data)>MAX_FILE:raise ValueError("HOLD: root hook too large")
    return data


def journal_dir_fd(rfd):
    try:os.mkdir(".fabrica",mode=0o700,dir_fd=rfd)
    except FileExistsError:pass
    return os.open(".fabrica",os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=rfd)


def journal_name(name): return "UAC004_"+name+".journal.json"


def make_journal(jfd,name,record):
    fd=os.open(journal_name(name),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=jfd)
    try:
        data=canonical(record)
        with os.fdopen(fd,"wb",closefd=False) as f:
            f.write(data);f.flush();os.fsync(fd)
    finally:os.close(fd)
    os.fsync(jfd)


def journal_record(jfd,name):
    fd=os.open(journal_name(name),os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=jfd)
    try:
        st=os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_size>8192:raise ValueError("HOLD: invalid root journal")
        r=json.loads(os.read(fd,8193))
    finally:os.close(fd)
    if (r.get("schema")!="fdf.uac004.journal/0.1" or r.get("target")!=name or
        not all(isinstance(r.get(k),str) and len(r[k])==64 for k in ("before","after","tail")) or
        not isinstance(r.get("before_length"),int)):
        raise ValueError("HOLD: untrusted root journal")
    return r


def append_guarded(root,name,expected_sha,tail):
    fcntl=require_platform()
    if not isinstance(tail,bytes) or not tail or len(tail)>8192:raise ValueError("HOLD: invalid append payload")
    rfd=root_fd(root)
    try:
        fd=file_fd(rfd,name)
        try:
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            raw=read_fd(fd)
            if sha(raw)!=expected_sha:raise ValueError("HOLD: root policy SHA drift")
            if len(raw)+len(tail)>MAX_FILE:raise ValueError("HOLD: root hook oversized")
            jfd=journal_dir_fd(rfd)
            try:
                record={"schema":"fdf.uac004.journal/0.1","target":name,"before":sha(raw),
                        "after":sha(raw+tail),"tail":sha(tail),"before_length":len(raw),
                        "authority":"OWNER_NOT_AUTHENTICATED","release":"HOLD"}
                make_journal(jfd,name,record)  # fsynced before target mutation
            finally:os.close(jfd)
            os.lseek(fd,0,os.SEEK_END)
            written=os.write(fd,tail)
            os.fsync(fd)
            if written!=len(tail) or sha(read_fd(fd))!=record["after"]:
                raise ValueError("HOLD: partial append; journal retained for review")
            return {"status":"APPENDED_SOURCE_VERIFIED_ONLY","journal":journal_name(name),
                    "before_sha256":record["before"],"after_sha256":record["after"],"release":"HOLD"}
        finally:os.close(fd)
    finally:os.close(rfd)


def inspect_recovery(root,name,*,restore=False):
    fcntl=require_platform()
    rfd=root_fd(root)
    try:
        jfd=journal_dir_fd(rfd)
        try:
            rec=journal_record(jfd,name)
            fd=file_fd(rfd,name)
            try:
                fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
                raw=read_fd(fd)
                state="PREPARED_NOT_APPLIED" if sha(raw)==rec["before"] else "APPENDED_INTACT" if sha(raw)==rec["after"] else "HOLD_POLICY_MODIFIED_OR_PARTIAL"
                if restore and state=="HOLD_POLICY_MODIFIED_OR_PARTIAL":
                    raise ValueError("HOLD: do not truncate modified/partial root policy")
                if restore:
                    if state=="APPENDED_INTACT":
                        os.ftruncate(fd,rec["before_length"])
                        os.fsync(fd)
                        if sha(read_fd(fd))!=rec["before"]:
                            raise ValueError("HOLD: root recovery hash mismatch")
                    os.unlink(journal_name(name),dir_fd=jfd)
                    os.fsync(jfd)
                return {"recovery_status":"RESTORED_AND_JOURNAL_CLEARED" if restore else state,"release":"HOLD"}
            finally:os.close(fd)
        finally:os.close(jfd)
    finally:os.close(rfd)
