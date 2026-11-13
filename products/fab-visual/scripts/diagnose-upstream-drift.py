#!/usr/bin/env python3
"""Narrow source-locked HTML serialization drift classifier for pinned Anatomy.

This tool never modifies inputs. Successful classification is *not* byte-parity:
any difference keeps the strict reproducible-build gate FAIL. A drift outside
explicitly reviewed numeric fields or packed orientation normal codes is a hard
FAIL_UNCLASSIFIED (exit 2), not silently tolerated.
"""
from __future__ import annotations
import argparse
import base64
import binascii
import hashlib
import json
import math
from pathlib import Path
import sys

PIN = '1482e8469b0a9e0d8cc18ea2740a01423d29ae80'
FILES = {
    'examples/raptor-engine/raptor-engine.html': ('D', 'cb2b7df8f24bf86fe870aa25598e348626af263332c553b90bd574dd029a257b'),
    'examples/raptor-engine/raptor-engine-light.html': ('D', '48f64b954b93567f1a5ca87fa823c34ae9e81842fa5b95512deba6b22b37a537'),
    'examples/turning-dial/turning-stress-light.html': ('DATA', 'e175e82f1bba087bb6031e375fb5da386f4f779e89e91a7864f7fc298b8b14e3'),
}
RAPTOR_ALLOWED = {'.V[2]', '.camera.k', '.camera.cam[2]', '.exit[1]'}
# Absolute values require interpreting the original builder's octave quantization.
# This is a *bounded diagnostic*, not a source/render acceptance threshold.
MAX_DELTA_NORMAL = 4e-5
MAX_RAPTOR_DELTA = 1e-12


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract(text: str, symbol: str):
    marker = 'const ' + symbol + ' = '
    if text.count(marker) != 1:
        raise ValueError('expected one '+marker)
    start = text.index(marker) + len(marker)
    value, n = json.JSONDecoder().raw_decode(text[start:])
    return value, text[:start], text[start+n:]


def changed_paths(a, b, prefix=''):
    if type(a) is not type(b):
        raise ValueError('type changed at '+prefix)
    if isinstance(a, dict):
        if a.keys() != b.keys():
            raise ValueError('keys changed at '+prefix)
        for key in a:
            yield from changed_paths(a[key], b[key], prefix+'.'+key)
    elif isinstance(a, list):
        if len(a) != len(b):
            raise ValueError('array length changed at '+prefix)
        for i, (x, y) in enumerate(zip(a, b)):
            yield from changed_paths(x, y, prefix+f'[{i}]')
    elif a != b:
        yield (prefix, a, b)


def oct_normal(u: int, v: int):
    x = u/65535*2-1
    y = v/65535*2-1
    z = 1-abs(x)-abs(y)
    if z < 0:
        x, y = (1-abs(y))*(1 if x >= 0 else -1), (1-abs(x))*(1 if y >= 0 else -1)
    length = math.sqrt(x*x+y*y+z*z) or 1
    return (x/length, y/length, z/length)


def verify_framed(a: str, b: str):
    if not isinstance(a, str) or not isinstance(b, str):
        raise ValueError('packed orientation not a string')
    try:
        old=base64.b64decode(a, validate=True)
        new=base64.b64decode(b, validate=True)
    except (ValueError, binascii.Error) as ex:
        raise ValueError('invalid base64 orientation data') from ex
    if len(old) != len(new) or len(old)%10:
        raise ValueError('changed packed record length')
    changed=[]
    for i in range(len(old)//10):
        p,q=old[10*i:10*(i+1)],new[10*i:10*(i+1)]
        if p == q:
            continue
        # 3 identity/owner indices then 2 octahedral quantized normal components.
        u=tuple(int.from_bytes(p[k:k+2],'big') for k in range(0,10,2))
        v=tuple(int.from_bytes(q[k:k+2],'big') for k in range(0,10,2))
        if u[:3]!=v[:3]:
            raise ValueError(f'part/group identity changed in packed record {i}')
        n1=oct_normal(*u[3:]);n2=oct_normal(*v[3:])
        d=math.sqrt(sum((x-y)**2 for x,y in zip(n1,n2)))
        if d>MAX_DELTA_NORMAL:
            raise ValueError(f'normal drift exceeds bound at record {i}: {d}')
        changed.append({'index':i,'identity':list(u[:3]),'old_oct':list(u[3:]),'new_oct':list(v[3:]),'normal_l2_delta':d})
    if len(changed) != 5:
        raise ValueError(f'unexpected changed record count {len(changed)} != source-locked 5')
    return {'packed_record_count':len(old)//10, 'packed_bytes':len(old), 'changed_records':changed,
            'count_changed_records':len(changed),
            'max_normal_l2_delta':max(x['normal_l2_delta'] for x in changed)}


def classify_one(path: str, baseline: Path, candidate: Path):
    symbol, source_sha = FILES[path]
    # Explicitly disallow symlink traversal, including ancestor directories.
    for root in (baseline,candidate):
        q=root
        while q != q.parent:
            if q.is_symlink():raise ValueError('symlink ancestor: '+str(q))
            q=q.parent
        t=root/path
        while t != root:
            if t.is_symlink():raise ValueError('symlink source path '+str(t))
            t=t.parent
    a=(baseline/path).read_bytes();b=(candidate/path).read_bytes()
    if digest(a) != source_sha:
        raise ValueError('baseline hash does not match pinned Git blob source for '+path)
    # Input always UTF-8 generated HTML; unexpected encoding blocks admission.
    src=a.decode('utf-8');reb=b.decode('utf-8')
    x,prefix,suffix=extract(src,symbol);y,prefix2,suffix2=extract(reb,symbol)
    if prefix!=prefix2 or suffix!=suffix2:
        raise ValueError('HTML code/markup changed outside source-locked data constant: '+path)
    if digest(a) == digest(b):
        return {'path':path,'baseline_sha256':source_sha,'rebuilt_sha256':digest(b),
                'byte_identical':True,'classification':'EXACT_BYTE_PARITY'}
    delta=list(changed_paths(x,y))
    if symbol == 'D':
        paths={d[0] for d in delta}
        if paths != RAPTOR_ALLOWED:
            raise ValueError('unexpected changed JSON paths '+str(sorted(paths)))
        diffs=[]
        for p,old,new in delta:
            if type(old) not in (int,float) or type(new) not in (int,float):
                raise ValueError('nonnumeric raptor field changed '+p)
            difference=abs(old-new)
            if not math.isfinite(difference) or difference>MAX_RAPTOR_DELTA:
                raise ValueError('raptor numeric drift out of bounds at '+p)
            diffs.append({'path':p,'old':old,'new':new,'absolute_delta':difference})
        return {'path':path,'baseline_sha256':source_sha,'rebuilt_sha256':digest(b),
                'byte_identical':False,'classification':'BOUNDED_CAMERA_FLOAT_SERIALIZATION',
                'outside_data_constant_identical':True,'changed_fields':diffs,
                'max_absolute_delta':max(z['absolute_delta'] for z in diffs)}
    if [p for p,_,_ in delta]!=['.framed.hand']:
        raise ValueError('unexpected changed packed data paths '+str([d[0] for d in delta]))
    detail=verify_framed(delta[0][1],delta[0][2])
    return {'path':path,'baseline_sha256':source_sha,'rebuilt_sha256':digest(b),
            'byte_identical':False,'classification':'BOUNDED_PACKED_OCT_NORMAL_DIFFERENCE',
            'outside_data_constant_identical':True,'unchanged_other_JSON_fields':True,**detail}


def run(baseline:Path,candidate:Path):
    report={'schema':'fab.visual.omega10b.drift.v1','upstream_commit':PIN,
            'inputs':{'baseline_root':str(baseline),'candidate_root':str(candidate)},
            'scope':'ONLY_THREE_KNOWN_UPSTREAM_COMMITTED_HTML_PAGES',
            'release':'HOLD','parity':'NOT_EVALUATED','diagnostic':'NOT_RUN','files':[]}
    try:
        for f in FILES:
            report['files'].append(classify_one(f,baseline,candidate))
        exact=all(x['byte_identical'] for x in report['files'])
        report['parity']='PASS' if exact else 'FAIL'
        report['diagnostic']='EXACT_PARITY' if exact else 'PASS_BOUNDED_NUMERIC_DIAGNOSIS'
        report['conclusion']='Bounding a decoded camera/normal difference does NOT establish visual, dynamic, PDF, 3D or scientific equivalence.'
        return report,0
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as ex:
        report['parity']='FAIL'
        report['diagnostic']='FAIL_UNCLASSIFIED'
        report['error']=str(ex)
        return report,2


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--rebuilt',type=Path,required=True)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    report,code=run(args.baseline,args.rebuilt)
    value=json.dumps(report,indent=2,sort_keys=True)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(value,encoding='utf8')
    print(value)
    sys.exit(code)

if __name__=='__main__':main()
