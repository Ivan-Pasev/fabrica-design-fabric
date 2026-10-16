"""Bounded FDF caller-project source-probe tests; no network or edits."""
import json, tempfile, unittest
from pathlib import Path
from tools.fdf_workspace_probe import scan

class TestProbe(unittest.TestCase):
    def test_observed_path_lines_and_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'src').mkdir()
            (p/'src'/'Home.tsx').write_text('export default () => <><img src="x.png"/><button><svg></svg></button></>')
            r=scan(p)
            self.assertEqual({x['rule'] for x in r['candidate_changes']},{'img_missing_alt','icon_button_name'})
            self.assertTrue(all(x['path']=='src/Home.tsx' and x['line']==1 for x in r['candidate_changes']))
            self.assertFalse(r['mutations_performed'])
    def test_existing_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'index.html').write_text('<img alt="Purpose" src="x"><button aria-label="Menu"><svg></svg></button>')
            self.assertFalse(scan(tmp)['candidate_changes'])
    def test_reduced_motion(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'styles.css').write_text('button {animation: pulse 1s}')
            self.assertEqual(scan(tmp)['candidate_changes'][0]['rule'],'reduced_motion_equivalence')
    def test_no_protected_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'.env').write_text('PRIVATE_SPECIAL_VALUE')
            (p/'node_modules').mkdir();(p/'node_modules'/'bad.html').write_text('PRIVATE_SPECIAL_VALUE')
            (p/'src.html').write_text('<img src="visible.png">')
            r=json.dumps(scan(p))
            self.assertNotIn('PRIVATE_SPECIAL_VALUE',r)
            self.assertNotIn('bad.html',r)
    def test_symlinks_not_followed(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            (Path(b)/'secret.html').write_text('<img>')
            (Path(a)/'external').symlink_to(b,target_is_directory=True)
            self.assertEqual(scan(a)['observed_files'],[])
    def test_too_large_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'large.html').write_text('x'*67000)
            self.assertEqual(scan(tmp)['skipped'][0]['reason'],'oversized')
    def test_no_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'index.html';p.write_text('<img>');before=p.read_bytes()
            scan(tmp)
            self.assertEqual(p.read_bytes(),before)
    def test_root_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            alias=Path(tmp).parent/(Path(tmp).name+'_alias')
            try:
                alias.symlink_to(tmp,target_is_directory=True)
                with self.assertRaises(ValueError):scan(alias)
            finally:alias.unlink(missing_ok=True)

if __name__=='__main__': unittest.main()
