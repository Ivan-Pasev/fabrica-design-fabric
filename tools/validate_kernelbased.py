#!/usr/bin/env python3
"""No-install source contract check; not a live IDE, security or runtime assessment."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read_json(path):
    p = ROOT / path
    assert p.is_file() and not p.is_symlink(), path
    return json.loads(p.read_text(encoding="utf-8"))

def verify():
    k = read_json(".kbi/kernel.kbi.json")
    l = read_json(".kbi/designskill-lattice.json")
    assert k["schema"] == "fdf.kernelbased-intelligence/0.2"
    assert k["meaning"] == "Kernel-Based Intelligence"
    assert k["target"] == "CALLER_IDE_ACTIVE_WORKSPACE"
    assert k["default_mode"] == "PROPOSE_ONLY"
    assert not any(k["permissions"][x] for x in ("write","install","git_push","deploy","auto_governance_mutation"))
    assert k["boundary"]["caller_project_policies_take_precedence"] is True
    assert l["schema"] == "fdf.designskill-lattice/0.2"
    assert l["target"] == "CALLER_IDE_ACTIVE_WORKSPACE"
    nodes = l["nodes"]
    by_id = {n["id"]:n for n in nodes}
    assert len(nodes) == len(by_id) == 15
    assert all(n["mode"]=="AUDIT_ONLY" and n["effects"]==[] for n in nodes)
    visiting=set(); visited=set()
    def visit(skill):
        assert skill in by_id and skill not in visiting
        if skill in visited:return
        visiting.add(skill)
        for dependency in by_id[skill]["depends_on"]: visit(dependency)
        visiting.remove(skill);visited.add(skill)
    for skill in by_id:visit(skill)
    for name in ("BOOTSTRAP.md","README.md","AGENTS.md","skills/fdf-design-fabric/SKILL.md"):
        p=ROOT/name
        assert p.is_file() and not p.is_symlink()
    assert "Kernel-Based Intelligence" in (ROOT/"AGENTS.md").read_text()
    assert "currently open" in (ROOT/"BOOTSTRAP.md").read_text()
    print("FDF source-only KBI/IDE contract PASS: 15 skill nodes, no auto mutation")
if __name__=="__main__": verify()
