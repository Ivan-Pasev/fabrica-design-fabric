#!/usr/bin/env python3
"""Bounded, read-only FDF source observations for the currently open IDE project.
Heuristic proposals only: not a parser, executor, security boundary, or WCAG audit.
"""
import argparse, hashlib, json, os, re
from pathlib import Path
SKIP={'.git','.next','.nuxt','.svelte-kit','node_modules','dist','build','coverage','.venv','venv','vendor','.secrets','.cache','.idea','.vscode','__tests__'}
EXT={'.tsx','.jsx','.html','.vue','.svelte','.css'}
MAX_BYTES=65536
MAX_FILES=120

def scan(project):
    root=Path(project).expanduser().absolute()
    if not root.is_dir() or root.is_symlink():raise ValueError('Expected real, non-symlink project directory')
    observed=[];changes=[];skipped=[];n=0
    for base,dirs,files in os.walk(root,topdown=True,followlinks=False):
        here=Path(base)
        dirs[:]=sorted(d for d in dirs if d not in SKIP and not d.startswith('.') and not (here/d).is_symlink()) if len(here.relative_to(root).parts)<5 else []
        for name in sorted(files):
            p=here/name; rel=p.relative_to(root).as_posix()
            if p.suffix.lower() not in EXT or p.is_symlink() or any(z in SKIP or z.startswith('.') for z in Path(rel).parts):continue
            if n>=MAX_FILES:break
            n+=1
            try:
                if p.stat().st_size>MAX_BYTES:skipped.append({'path':rel,'reason':'oversized'});continue
                raw=p.read_bytes()
                if b'\0' in raw:skipped.append({'path':rel,'reason':'binary'});continue
                content=raw.decode('utf-8')
            except (OSError,UnicodeError):skipped.append({'path':rel,'reason':'unreadable'});continue
            observed.append({'path':rel,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
            if p.suffix.lower()=='.css':
                if ('animation:' in content or '@keyframes' in content) and 'prefers-reduced-motion' not in content:
                    changes.append({'path':rel,'line':1,'rule':'reduced_motion_equivalence',
                      'proposal':'Audit CSS animations; provide prefers-reduced-motion functional parity.',
                      'source_excerpt_sha256':hashlib.sha256(raw).hexdigest(),'status':'HUMAN_REVIEW_REQUIRED'})
                continue
            for m in list(re.finditer(r'<img\b[^>]*>',content,re.I|re.S))[:5]:
                if not re.search(r'\balt\s*=',m.group(),re.I):
                    changes.append({'path':rel,'line':content.count('\n',0,m.start())+1,'rule':'img_missing_alt',
                        'proposal':'Determine image purpose; supply accurate alt text or alt="" when decorative.',
                        'source_excerpt_sha256':hashlib.sha256(m.group().encode()).hexdigest(),'status':'HUMAN_REVIEW_REQUIRED'})
            for m in list(re.finditer(r'<button\b[^>]*>\s*(?:<svg\b[\s\S]*?</svg>\s*)+</button\s*>',content,re.I))[:5]:
                if not re.search(r'\baria-label(?:ledby)?\s*=',m.group(),re.I):
                    changes.append({'path':rel,'line':content.count('\n',0,m.start())+1,'rule':'icon_button_name',
                        'proposal':'Add a meaningful accessible name that describes the button action.',
                        'source_excerpt_sha256':hashlib.sha256(m.group().encode()).hexdigest(),'status':'HUMAN_REVIEW_REQUIRED'})
    return {'schema':'fdf.caller-project-design-proposal/0.1','target':'CALLER_IDE_ACTIVE_WORKSPACE',
        'mode':'PROPOSE_ONLY','observed_files':observed,'candidate_changes':changes,'skipped':skipped,
        'mutations_performed':False,'tests_executed':[],'approval_required_for_mutation':True,
        'limitations':['Regex heuristics, not AST or complete design audit','No file mutation or target code execution',
            'Only source hashes and file anchors emitted, not source contents',
            'Real IDE URL handoff and actual quality improvement still unverified']}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--project',default='.')
    print(json.dumps(scan(parser.parse_args().project),indent=2,sort_keys=True))
