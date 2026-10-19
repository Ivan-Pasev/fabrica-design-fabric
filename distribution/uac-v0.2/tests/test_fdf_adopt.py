import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'fdf_adopt.py'
spec=importlib.util.spec_from_file_location('fdf_adopt',TOOL)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Adoption(unittest.TestCase):
    def setUp(self):
        self.ctx=tempfile.TemporaryDirectory();self.addCleanup(self.ctx.cleanup)
        self.root=Path(self.ctx.name)

    def plan(self, plats=('cursor','codex','gemini','antigravity','chatgpt','aistudio'), hooks='none'):
        return m.generate_plan(self.root,plats,hooks)[0]

    def test_inspection_never_writes(self):
        (self.root/'AGENTS.md').write_text('EXISTING INSTRUCTIONS')
        before=sorted(p.name for p in self.root.iterdir())
        p=self.plan()
        self.assertEqual(sorted(q.name for q in self.root.iterdir()),before)
        self.assertFalse(p['projectdna']['policy_semantics_read'])
        self.assertEqual(p['projectdna']['known_policies'][0]['path'],'AGENTS.md')

    def test_all_six_adapters_generated(self):
        p,_=m.generate_plan(self.root,m.PLATFORMS,'none')
        paths={a['path'] for a in p['actions']}
        for path in ('.cursor/rules/fabrica-design-fabric.mdc','.agents/rules/fabrica-design-fabric.md',
                     '.gemini/skills/fabrica-design-fabric/SKILL.md','.fabrica/CHATGPT_PROJECT_INSTRUCTIONS.md',
                     '.fabrica/AI_STUDIO_BUILD_PROMPT.md'):
            self.assertIn(path,paths)
        self.assertNotIn('AGENTS.md', paths)
        self.assertNotIn('GEMINI.md', paths)

    def test_apply_requires_exact_digest(self):
        p=self.plan()
        with self.assertRaisesRegex(ValueError,'plan changed'):
            m.apply(self.root,'0'*64,m.PLATFORMS,'none')
        self.assertFalse((self.root/'.fabrica').exists())
        self.assertTrue(m.apply(self.root,p['plan_sha256'],m.PLATFORMS,'none')['applied'])
        self.assertEqual(m.verify(self.root)['verdict'],'INSTALLED_SOURCE_HASHES_MATCH')

    def test_existing_project_rules_untouched(self):
        old=b'HOST_LAW_FIRST\nPRIVATE_NON_SECRET\n'
        (self.root/'AGENTS.md').write_bytes(old)
        (self.root/'GEMINI.md').write_text('Gemini root existing')
        p=self.plan()
        m.apply(self.root,p['plan_sha256'],m.PLATFORMS,'none')
        self.assertEqual((self.root/'AGENTS.md').read_bytes(),old)
        self.assertEqual((self.root/'GEMINI.md').read_text(),'Gemini root existing')

    def test_root_append_surgical_roundtrip(self):
        (self.root/'AGENTS.md').write_bytes(b'FIRST AUTHORITY\r\nNo shortcuts')
        (self.root/'GEMINI.md').write_bytes(b'Keep old context\n')
        old1=(self.root/'AGENTS.md').read_bytes();old2=(self.root/'GEMINI.md').read_bytes()
        p=self.plan(hooks='append')
        self.assertEqual({a['path'] for a in p['actions'] if a['kind']=='root_hook'},{'AGENTS.md','GEMINI.md'})
        m.apply(self.root,p['plan_sha256'],m.PLATFORMS,'append')
        self.assertTrue((self.root/'AGENTS.md').read_bytes().startswith(old1))
        self.assertIn(m.BEGIN.encode(),(self.root/'GEMINI.md').read_bytes())
        self.assertEqual(m.verify(self.root)['changed'],[])
        m.rollback(self.root,p['plan_sha256'])
        self.assertEqual((self.root/'AGENTS.md').read_bytes(),old1)
        self.assertEqual((self.root/'GEMINI.md').read_bytes(),old2)
        self.assertFalse((self.root/'.fabrica/ADOPTION_MANIFEST.json').exists())

    def test_root_create_roundtrip(self):
        p=self.plan(hooks='append')
        m.apply(self.root,p['plan_sha256'],m.PLATFORMS,'append')
        self.assertTrue((self.root/'AGENTS.md').exists())
        self.assertTrue((self.root/'GEMINI.md').exists())
        m.rollback(self.root,p['plan_sha256'])
        self.assertFalse((self.root/'AGENTS.md').exists())
        self.assertFalse((self.root/'GEMINI.md').exists())

    def test_conflict_blocks_all(self):
        p=self.root/'.cursor/rules/fabrica-design-fabric.mdc'
        p.parent.mkdir(parents=True)
        p.write_text('MY CUSTOM RULE')
        plan=self.plan()
        self.assertIn('.cursor/rules/fabrica-design-fabric.mdc',plan['collisions'])
        with self.assertRaisesRegex(ValueError,'conflicts'):
            m.apply(self.root,plan['plan_sha256'],m.PLATFORMS,'none')
        self.assertEqual(p.read_text(),'MY CUSTOM RULE')
        self.assertFalse((self.root/'.fabrica').exists())

    def test_existing_marker_blocks_root_append(self):
        (self.root/'AGENTS.md').write_text(m.BEGIN+'\nmy modified section')
        p=self.plan(hooks='append')
        self.assertIn('AGENTS.md',p['collisions'])

    def test_drift_blocks_apply(self):
        p=self.plan(hooks='append')
        (self.root/'AGENTS.md').write_text('new owner rules')
        with self.assertRaisesRegex(ValueError,'plan changed'):
            m.apply(self.root,p['plan_sha256'],m.PLATFORMS,'append')

    def test_modified_managed_file_blocks_rollback(self):
        p=self.plan()
        m.apply(self.root,p['plan_sha256'],m.PLATFORMS,'none')
        target=self.root/'.fabrica/CONTRACT.md';target.write_text('new host edits')
        self.assertIn('.fabrica/CONTRACT.md',m.verify(self.root)['changed'])
        with self.assertRaisesRegex(ValueError,'modified install paths'):
            m.rollback(self.root,p['plan_sha256'])
        self.assertEqual(target.read_text(),'new host edits')

    def test_wrong_rollback_digest_rejected(self):
        p=self.plan();m.apply(self.root,p['plan_sha256'],m.PLATFORMS,'none')
        with self.assertRaisesRegex(ValueError,'wrong installation plan'):
            m.rollback(self.root,'0'*64)

    def test_symlink_target_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            (self.root/'.cursor').symlink_to(tmp)
            with self.assertRaisesRegex(ValueError,'symlink'):
                self.plan()

    def test_symlink_root_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            link=self.root/'alias';link.symlink_to(tmp,target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'symlink'):
                m.require_root(link)

    def test_selected_adapter_only(self):
        p=self.plan(plats=('cursor',))
        a={v['path'] for v in p['actions']}
        self.assertIn('.cursor/rules/fabrica-design-fabric.mdc',a)
        self.assertNotIn('.agents/rules/fabrica-design-fabric.md',a)
        self.assertNotIn('.gemini/skills/fabrica-design-fabric/SKILL.md',a)
        self.assertNotIn('AGENTS.md',a)

    def test_phase_and_frontend_signals_no_script_execution(self):
        (self.root/'package.json').write_text(json.dumps({'scripts':{'postinstall':'exit 14'},'dependencies':{'react':'1.0','next':'1.0'}}))
        signals=m.detect(self.root)
        self.assertIn('react',signals['ui_signals'])
        self.assertIn('next',signals['ui_signals'])
        self.assertIn('node',signals['tech_signals'])

    def test_no_network_or_dependencies_in_contract(self):
        p,t=m.generate_plan(self.root,m.PLATFORMS,'none')
        contract=t['.fabrica/CONTRACT.md']
        self.assertIn('Default PROPOSE_ONLY',contract)
        self.assertIn('No edits, installs',contract)
        self.assertIn('are automatically mounted, read or executed',contract)

    def test_cli_plan_and_apply_and_verify(self):
        base=[sys.executable,str(TOOL)]
        args=['--project',str(self.root),'--platforms','cursor,codex']
        r=subprocess.run(base+['plan']+args,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
        sha=json.loads(r.stdout)['plan_sha256']
        q=subprocess.run(base+['apply']+args+['--approve-plan',sha],capture_output=True,text=True)
        self.assertEqual(q.returncode,0,q.stderr)
        v=subprocess.run(base+['verify']+args,capture_output=True,text=True)
        self.assertEqual(json.loads(v.stdout)['verdict'],'INSTALLED_SOURCE_HASHES_MATCH')

    def test_existing_policy_symlink_refusal(self):
        with tempfile.TemporaryDirectory() as t:
            target=Path(t)/'root-policy';target.write_text('secret value')
            (self.root/'AGENTS.md').symlink_to(target)
            with self.assertRaisesRegex(ValueError,'symlink'):
                self.plan()

    def test_root_hooks_selective(self):
        a=self.plan(plats=('cursor','chatgpt'),hooks='append')
        self.assertNotIn('AGENTS.md',{x['path'] for x in a['actions']})
        self.assertNotIn('GEMINI.md',{x['path'] for x in a['actions']})

    def test_managed_files_do_not_repeat_upstream_skills(self):
        p,t=m.generate_plan(self.root,m.PLATFORMS,'none')
        raw='\n'.join(t.values())
        self.assertNotIn('npx skills@latest',raw)
        self.assertNotIn('curl | sh',raw)

if __name__=='__main__':unittest.main()
