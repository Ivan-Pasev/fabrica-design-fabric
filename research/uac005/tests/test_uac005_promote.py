import importlib.util, hashlib, json, subprocess, tempfile, unittest, zipfile
from pathlib import Path
s=Path(__file__).resolve().parents[1]/'tools/uac005_promote.py'
x=importlib.util.spec_from_file_location('uac005',s)
m=importlib.util.module_from_spec(x);x.loader.exec_module(m)

class Promoter(unittest.TestCase):
 def setUp(self):
  c=tempfile.TemporaryDirectory();self.addCleanup(c.cleanup)
  self.root=Path(c.name)/'checkout';self.root.mkdir()
  subprocess.run(['git','init','-q',str(self.root)],check=True)
  subprocess.run(['git','-C',str(self.root),'config','user.email','test@example.org'],check=True)
  subprocess.run(['git','-C',str(self.root),'config','user.name','test'],check=True)
  (self.root/'README.md').write_text('existing host')
  subprocess.run(['git','-C',str(self.root),'add','README.md'],check=True)
  subprocess.run(['git','-C',str(self.root),'commit','-qm','initial'],check=True)
  self.zip=Path(c.name)/'test.zip'
  data={f'tools/test_{i:02d}.py':f'print({i})\n'.encode() for i in range(14)}
  manifest={'schema':'fdf.source-manifest/0.2','entry_count':14,'files':[{'path':k,'bytes':len(v),'sha256':m.digest(v)} for k,v in data.items()]}
  with zipfile.ZipFile(self.zip,'w',compression=zipfile.ZIP_DEFLATED) as z:
   z.writestr('FABRICA_MANIFEST.json',json.dumps(manifest))
   for k,v in data.items():z.writestr(k,v)
  self.original=m.PIN;m.PIN=m.digest(self.zip.read_bytes())
  self.addCleanup(lambda:setattr(m,'PIN',self.original))
 def test_plan_readonly(self):
  p=m.plan(self.zip,self.root)
  self.assertEqual(len(p['files']),14)
  self.assertFalse((self.root/'distribution').exists())
 def test_apply_verify_no_git_commit(self):
  p=m.plan(self.zip,self.root)
  out=m.apply(self.zip,self.root,p['plan_sha256'])
  self.assertEqual(out['files_imported'],14)
  self.assertEqual(m.verify(self.root)['source_files_verified'],14)
  self.assertEqual((self.root/'README.md').read_text(),'existing host')
  self.assertTrue(subprocess.run(['git','-C',str(self.root),'status','--porcelain'],capture_output=True,text=True).stdout.strip())
 def test_wrong_digest_refused(self):
  with self.assertRaisesRegex(ValueError,'approval digest'):m.apply(self.zip,self.root,'0'*64)
  self.assertFalse((self.root/'distribution').exists())
 def test_refuse_dirty(self):
  (self.root/'scratch.txt').write_text('uncommitted')
  with self.assertRaisesRegex(ValueError,'existing changes'):m.plan(self.zip,self.root)
 def test_refuse_existing_dest(self):
  (self.root/'distribution').mkdir();(self.root/'distribution/uac-v0.2').mkdir()
  with self.assertRaisesRegex(ValueError,'existing output'):m.plan(self.zip,self.root)
 def test_refuse_tamper(self):
  p=m.plan(self.zip,self.root);m.apply(self.zip,self.root,p['plan_sha256'])
  (self.root/'distribution/uac-v0.2/tools/test_00.py').write_text('changed')
  with self.assertRaisesRegex(ValueError,'SHA drift'):m.verify(self.root)
 def test_refuse_symlinked_distribution(self):
  (self.root/'distribution').symlink_to(self.root)
  with self.assertRaisesRegex(ValueError,'existing changes|unsafe distribution'):m.plan(self.zip,self.root)
 def test_refuse_archive_hash_drift(self):
  m.PIN='0'*64
  with self.assertRaisesRegex(ValueError,'ZIP SHA mismatch'):m.plan(self.zip,self.root)
if __name__=='__main__':unittest.main()
