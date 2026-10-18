#!/usr/bin/env python3
"""UAC-002 minimal GitHub-side source-only FDF() preview. Never writes project files."""
import argparse
import json
from pathlib import Path
POLICIES=("AGENTS.md","GEMINI.md","CLAUDE.md","AI_CRITICAL.md",".cursorrules",".cursor/rules",".agents/rules",".agents/skills")
ALWAYS=("fdf-project-observer","fdf-governance-gate","fdf-evolution-planner","fdf-verification-engine")
def inspect(path):
    root=Path(path).absolute()
    if not root.is_dir() or root.is_symlink():raise ValueError("HOLD project root is missing or symlinked")
    existing=[]
    for rel in POLICIES:
        cur=root
        for seg in rel.split("/"):
            cur=cur/seg
            if cur.is_symlink(): raise ValueError("HOLD symlinked policy path")
        if cur.exists():existing.append(rel)
    candidates={"package.json","pyproject.toml","Cargo.toml","go.mod","index.html","src","app","pages","public","research","papers"}
    names={p.name for i,p in enumerate(root.iterdir()) if i<2048 and not p.is_symlink() and p.name in candidates}
    ui=bool(names.intersection({"index.html","src","app","pages","public"}))
    code=bool(names.intersection({"package.json","pyproject.toml","Cargo.toml","go.mod"}))
    research=bool(names.intersection({"research","papers"}))
    selected=list(ALWAYS)
    if ui:selected+=["fdf-design-critic","fdf-accessibility-review","fdf-motion-director"]
    if code:selected.append("fdf-runtime-architecture")
    if research:selected.append("fdf-research-provenance")
    return {"schema":"fdf.uac002.preview/0.2","mode":"AUGMENT_EXISTING_UNVERIFIED" if existing else "SCAFFOLD_ADVISORY_KERNEL","found_policies":existing,"observed_top_level_signals":sorted(names),"selected_first_party_skills":selected,"external_skills_installed":False,"files_written":False,"actual_ide_verified":False,"owner_approved":False,"release":"HOLD"}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=("FDF",))
    p.add_argument("--project",required=True)
    a=p.parse_args()
    try:print(json.dumps(inspect(a.project),indent=2,sort_keys=True))
    except (OSError,ValueError) as e:p.exit(2,str(e)+"\n")
if __name__=="__main__":main()
