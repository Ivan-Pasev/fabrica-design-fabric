import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'tools'))
import fdf_adopt as adopt
import fdf_kernel as kernel

class Kernel(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name)
 def plan(self, platforms=('codex','antigravity','gemini','cursor','chatgpt','aistudio')):
  return adopt.generate_plan(self.root,platforms,'none')
 def test_empty_root_advisory_scaffold(self):
  p,files=self.plan(); self.assertEqual(kernel.select(p['projectdna'])['mode'],'SCAFFOLD_ADVISORY_KERNEL')
  self.assertIn('.fabrica/KERNEL.md',files)
  self.assertIn('.fabrica/STATE_AND_HANDOFF.md',files)
  self.assertIn('.agents/skills/fdf-governance-gate/SKILL.md',files)
 def test_existing_policy_kernel_augmented_not_overwritten(self):
  old=b'LOCAL ROOT AUTHORITATIVE\n';(self.root/'AGENTS.md').write_bytes(old)
  p,files=self.plan();self.assertEqual(kernel.select(p['projectdna'])['mode'],'AUGMENT_EXISTING_UNVERIFIED')
  adopt.apply(self.root,p['plan_sha256'],adopt.PLATFORMS,'none')
  self.assertEqual((self.root/'AGENTS.md').read_bytes(),old)
  adopt.rollback(self.root,p['plan_sha256']);self.assertEqual((self.root/'AGENTS.md').read_bytes(),old)
 def test_ui_skills_selected_by_grounded_signal(self):
  (self.root/'package.json').write_text(json.dumps({'dependencies':{'react':'^19'}}))
  p,files=self.plan();skills={v['name'] for v in kernel.select(p['projectdna'])['selected']}
  self.assertIn('fdf-accessibility-review',skills)
  self.assertIn('fdf-motion-director',skills)
  self.assertIn('.gemini/skills/fdf-design-critic/SKILL.md',files)
 def test_research_signal_selects_traceability(self):
  (self.root/"research").mkdir()
  p,files=self.plan();self.assertIn("fdf-research-provenance",{x["name"] for x in kernel.select(p["projectdna"])["selected"]})
  self.assertIn(".agents/skills/fdf-research-provenance/SKILL.md",files)
 def test_nonui_skills_not_forced(self):
  p,files=self.plan();self.assertNotIn('.agents/skills/fdf-design-critic/SKILL.md',files)
 def test_source_only_cli_FDF(self):
  q=subprocess.run([sys.executable,str(BASE/'tools/fdf.py'),'FDF','--project',str(self.root)],capture_output=True,text=True)
  self.assertEqual(q.returncode,0,q.stderr)
  o=json.loads(q.stdout);self.assertEqual(o['command'],'FDF()');self.assertFalse(o['files_written']);self.assertFalse((self.root/'.fabrica').exists())
 def test_plan_apply_verify_rollback_roundtrip(self):
  p,files=self.plan();adopt.apply(self.root,p['plan_sha256'],adopt.PLATFORMS,'none')
  self.assertEqual(adopt.verify(self.root)['verdict'],'INSTALLED_SOURCE_HASHES_MATCH')
  self.assertTrue((self.root/'.fabrica/SKILL_LATTICE.json').exists())
  adopt.rollback(self.root,p['plan_sha256']);self.assertFalse((self.root/'.fabrica/ADOPTION_MANIFEST.json').exists())
 def test_no_workflows_Antigravity_deprecation(self):
  _,files=self.plan();self.assertFalse(any('.agents/workflows/' in x for x in files))
  x=files['.agents/rules/fabrica-design-fabric.md'];self.assertIn('trigger: model_decision',x)
 def test_cloud_manual_not_auto_loaded(self):
  _,files=self.plan();self.assertIn('manual',files['.fabrica/CHATGPT_FDF_INJECTION.md'])
  self.assertIn('Import approved',files['.fabrica/AISTUDIO_FDF_INJECTION.md'])
 def test_existing_custom_skill_collision_holds(self):
  p=self.root/'.agents/skills/fdf-evolution-planner/SKILL.md';p.parent.mkdir(parents=True);p.write_text('old')
  result,_=self.plan();self.assertIn('.agents/skills/fdf-evolution-planner/SKILL.md',result['collisions'])
 def test_upstream_not_vendored_and_no_mutable_install(self):
  p,files=self.plan();texts='\n'.join(files.values())
  self.assertNotIn('npx skills@latest',texts)
  self.assertEqual(kernel.select(p['projectdna'])['upstream_optional']['mode'],'REFERENCE_ONLY_NOT_INSTALLED')
 def test_scoring_skills_unique(self):
  for x in ({},{'ui_signals':['react']},{'tech_signals':['node']},{'ui_signals':['react'],'tech_signals':['node']}):
   v=kernel.select(x);names=[y['name'] for y in v['selected']];self.assertEqual(len(names),len(set(names)))
 def test_new_skill_frontmatter(self):
  _,files=self.plan();s=files['.agents/skills/fdf-governance-gate/SKILL.md']
  self.assertTrue(s.startswith('---\nname:'))
  self.assertIn('description:',s)
 def test_evolve_is_proposal_only(self):
  q=subprocess.run([sys.executable,str(BASE/'tools/fdf.py'),'evolve','--project',str(self.root)],capture_output=True,text=True)
  self.assertEqual(q.returncode,0,q.stderr);v=json.loads(q.stdout)
  self.assertFalse(v['writes_performed']);self.assertEqual(v['human_decision'],'PENDING_NOT_GIVEN')
 def test_tamper_refuses_rollback(self):
  p,_=self.plan();adopt.apply(self.root,p['plan_sha256'],adopt.PLATFORMS,'none')
  (self.root/'.fabrica/KERNEL.md').write_text('edited by host')
  with self.assertRaisesRegex(ValueError,'modified install paths'):
   adopt.rollback(self.root,p['plan_sha256'])
 def test_no_root_policy_without_root_hooks(self):
  p,_=self.plan();self.assertNotIn('AGENTS.md',{v['path'] for v in p['actions']});self.assertNotIn('GEMINI.md',{v['path'] for v in p['actions']})
 def test_multi_surface_skill_lattice_matches(self):
  _,files=self.plan();a=files['.agents/skills/fdf-governance-gate/SKILL.md'];b=files['.gemini/skills/fdf-governance-gate/SKILL.md'];self.assertEqual(a,b)

if __name__=='__main__':unittest.main()
