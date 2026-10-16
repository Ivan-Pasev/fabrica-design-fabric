"""R28 source-binding / stale proposal failure cases."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from tools.fdf_workspace_probe import scan
from tools.fdf_proposal_compiler import compile_plan

class ProposalDNATests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'pages').mkdir()
        (self.root/'pages'/'home.tsx').write_text('function Home(){return <><img src="x"/><button><svg></svg></button></>}',encoding='utf8')
        (self.root/'motion.css').write_text('.hero {animation: shift 2s linear;}',encoding='utf8')
        self.receipt=scan(self.root)
    def test_three_source_bound_proposals(self):
        p=compile_plan(self.root,self.receipt)
        self.assertEqual(len(p['proposals']),3)
        self.assertFalse(p['mutations_performed'])
        self.assertTrue(all(z['executable_patch'] is None and not z['owner_authorized'] for z in p['proposals']))
    def test_source_byte_change_denied(self):
        (self.root/'pages'/'home.tsx').write_text('changed!')
        with self.assertRaisesRegex(ValueError,'stale'):compile_plan(self.root,self.receipt)
    def test_source_deleted_denied(self):
        (self.root/'motion.css').unlink()
        with self.assertRaises(ValueError):compile_plan(self.root,self.receipt)
    def test_forged_file_path_denied(self):
        x=copy.deepcopy(self.receipt);x['observed_files'][0]['path']='../../etc/passwd'
        with self.assertRaises(ValueError):compile_plan(self.root,x)
    def test_forged_line_denied(self):
        x=copy.deepcopy(self.receipt);x['candidate_changes'][0]['line']=77
        with self.assertRaises(ValueError):compile_plan(self.root,x)
    def test_forged_rule_denied(self):
        x=copy.deepcopy(self.receipt);x['candidate_changes'][0]['rule']='approve_prod_release'
        with self.assertRaises(ValueError):compile_plan(self.root,x)
    def test_forged_digest_denied(self):
        x=copy.deepcopy(self.receipt);x['candidate_changes'][0]['source_excerpt_sha256']='f'*64
        with self.assertRaises(ValueError):compile_plan(self.root,x)
    def test_inflated_permission_denied(self):
        x=copy.deepcopy(self.receipt);x['mutations_performed']=True
        with self.assertRaises(ValueError):compile_plan(self.root,x)
    def test_wrong_role_denied(self):
        x=copy.deepcopy(self.receipt);x['target']='FDF_REPOSITORY'
        with self.assertRaises(ValueError):compile_plan(self.root,x)
    def test_duplicate_observation_denied(self):
        x=copy.deepcopy(self.receipt);x['candidate_changes'].append(copy.deepcopy(x['candidate_changes'][0]))
        with self.assertRaises(ValueError):compile_plan(self.root,x)
    def test_no_secret_read_or_edit(self):
        (self.root/'.env').write_text('SUPER_SECRET_VALUE')
        a=(self.root/'pages'/'home.tsx').read_bytes();b=(self.root/'motion.css').read_bytes()
        p=json.dumps(compile_plan(self.root,self.receipt))
        self.assertNotIn('SUPER_SECRET_VALUE',p)
        self.assertEqual(a,(self.root/'pages'/'home.tsx').read_bytes())
        self.assertEqual(b,(self.root/'motion.css').read_bytes())
    def test_cli_live_read_only(self):
        import subprocess, sys
        script=Path(__file__).resolve().parents[1]/'tools'/'fdf_proposal_compiler.py'
        before=(self.root/'pages'/'home.tsx').read_bytes()
        proc=subprocess.run([sys.executable,str(script),'--project',str(self.root),'--live'],check=True,capture_output=True,text=True)
        self.assertEqual(len(json.loads(proc.stdout)['proposals']),3)
        self.assertEqual(before,(self.root/'pages'/'home.tsx').read_bytes())
    def test_existing_semantics_not_automatically_invented(self):
        p=compile_plan(self.root,self.receipt)
        self.assertTrue(all(x['semantic_questions'] for x in p['proposals']))
        self.assertTrue(all('PENDING_HUMAN_CONTEXT'==x['status'] for x in p['proposals']))

if __name__=='__main__':unittest.main()
