"""Controlled fixture rehearsal only, never an actual owner IDE trial."""
import importlib.util, tempfile, json, hashlib
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'tools'/'fdf_adopt.py'; spec=importlib.util.spec_from_file_location('fdf_adopt',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
results=[]
for name, policy_files, plats, hooks in [
 ('new-project',{},('cursor','codex','gemini','antigravity','chatgpt','aistudio'),'append'),
 ('mature-project',{'AGENTS.md':'EXISTING HOST MASTER\n# Existing Priority\nResearch integrity FIRST.\n','GEMINI.md':'Existing Gemini hierarchy\n','CLAUDE.md':'Existing developer rules\n','package.json':'{"dependencies":{"react":"18.0.0","next":"15.0.0"},"scripts":{"preinstall":"exit 33"}}'},('cursor','codex','gemini','antigravity','chatgpt','aistudio'),'append'),
 ('cursor-only',{'AGENTS.md':'Do not edit without authority\n'},('cursor',),'none'),
]:
    with tempfile.TemporaryDirectory(prefix='fdf-fixture-') as td:
        root=Path(td)
        for path,data in policy_files.items():
            p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
        original={path:(root/path).read_bytes() for path in policy_files}
        plan, _=m.generate_plan(root,plats,hooks)
        a=m.apply(root,plan['plan_sha256'],plats,hooks)
        verification=m.verify(root)
        rolled=m.rollback(root,plan['plan_sha256'])
        assert all((root/path).read_bytes()==payload for path,payload in original.items())
        assert not (root/'.fabrica/ADOPTION_MANIFEST.json').exists()
        results.append({'name':name,'platforms':list(plats),'root_hooks':hooks,'plan_action_count':len(plan['actions']),
                        'plan_collisions':plan['collisions'],'applied':a['applied'],
                        'verified':verification['verdict'],'rolled_back':rolled['rolled_back'],
                        'all_existing_root_files_byte_identical_after_rollback':True,
                        'source_execution':'NONE','real_ide_verified':False,'owner_authorized_external':'NOT_ATTESTED'})
record={'schema':'fdf.adoption.scenario-evidence/0.1','status':'SYNTHETIC_FIXTURE_ONLY','scenarios':results}
(Path(__file__).resolve().parent/'SCENARIO_REPLAY.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps(record,indent=2,sort_keys=True))
