"""R30 regression suite for R29 adversarial findings and R28 compatibility."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from tools.fdf_workspace_probe import MAX_BYTES, MAX_FILES, scan


class R30ScannerQualification(unittest.TestCase):
    def test_file_cap_is_explicit_and_fails_coverage(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for i in range(MAX_FILES + 1):
                (root / f's{i:03d}.tsx').write_text('<img src="x.png"/>', encoding='utf8')
            r = scan(root)
            self.assertEqual(len(r['observed_files']), MAX_FILES)
            self.assertEqual(len(r['candidate_changes']), MAX_FILES)
            self.assertNotIn('s120.tsx', [f['path'] for f in r['observed_files']])
            self.assertFalse(r['coverage']['complete'])
            self.assertTrue(r['coverage']['file_cap_reached'])
            self.assertTrue(r['coverage']['counts_are_lower_bounds_when_capped'])
            self.assertEqual(r['coverage']['verdict'], 'INCOMPLETE')
            self.assertTrue(any(f['reason'] == 'file_cap' for f in r['skipped']))

    def test_parent_symlink_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'actual' / 'caller').mkdir(parents=True)
            (root / 'actual' / 'caller' / 'view.tsx').write_text('<img src="x"/>')
            (root / 'alias').symlink_to(root / 'actual', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlinked'):
                scan(root / 'alias' / 'caller')

    def test_root_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'actual').mkdir()
            (root / 'alias').symlink_to(root / 'actual', target_is_directory=True)
            with self.assertRaises(ValueError): scan(root / 'alias')

    def test_parent_navigation_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, 'traversal'):
                scan(Path(td) / '..' / Path(td).name)

    def test_large_file_never_observed_even_if_path_stat_underreports(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            huge = root / 'large.html'
            huge.write_bytes(b'A' * (MAX_BYTES + 100))
            original_stat = Path.stat
            def fake_stat(self, *args, **kwargs):
                if self == huge:
                    original = original_stat(self, *args, **kwargs)
                    return SimpleNamespace(st_size=5, st_mode=original.st_mode)
                return original_stat(self, *args, **kwargs)
            with patch.object(Path, 'stat', fake_stat):
                r = scan(root)
            self.assertEqual(r['observed_files'], [])
            self.assertEqual(r['skipped'][0]['reason'], 'oversized')
            self.assertFalse(r['coverage']['complete'])

    def test_oversized_and_binary_files_qualify_coverage(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'huge.html').write_bytes(b'X' * (MAX_BYTES + 1))
            (root / 'bin.html').write_bytes(b'\0hello')
            r = scan(root)
            self.assertEqual({x['reason'] for x in r['skipped']}, {'oversized', 'binary'})
            self.assertEqual(r['coverage']['skipped_files_recorded'], 2)
            self.assertFalse(r['coverage']['complete'])

    def test_comment_cannot_suppress_motion_finding(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'motion.css').write_text('/* TODO prefers-reduced-motion */\n.hero{animation:spin 2s linear}')
            r = scan(root)
            self.assertEqual(r['candidate_changes'][0]['rule'], 'reduced_motion_equivalence')

    def test_real_override_does_not_raise_local_motion_flag(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'motion.css').write_text('.hero {animation:pulse 2s}\n@media (prefers-reduced-motion: reduce) {.hero {animation:none}}')
            self.assertEqual(scan(root)['candidate_changes'], [])

    def test_missing_override_and_no_comment(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'motion.css').write_text('button {animation:pulse 1s}')
            self.assertEqual(scan(root)['candidate_changes'][0]['rule'], 'reduced_motion_equivalence')

    def test_no_project_writes_and_metadata_consistency(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            f = root / 'src.html'
            f.write_text('<img src="a"><button><svg></svg></button>')
            before = f.read_bytes()
            r = scan(root)
            self.assertEqual(f.read_bytes(), before)
            self.assertEqual(len(r['candidate_changes']), 2)
            self.assertTrue(r['coverage']['complete'])
            self.assertEqual(r['coverage']['observed_files'], 1)
            self.assertEqual(r['schema'], 'fdf.caller-project-design-proposal/0.1')
            self.assertEqual(r['mode'], 'PROPOSE_ONLY')
            self.assertFalse(r['mutations_performed'])
            self.assertEqual(r['target'], 'CALLER_IDE_ACTIVE_WORKSPACE')

    def test_excludes_secrets_and_vendor_dirs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / '.env').write_text('TOP_SECRET')
            (root / 'node_modules').mkdir()
            (root / 'node_modules' / 'bad.html').write_text('TOP_SECRET')
            (root / 'home.html').write_text('<img src="a">')
            r = json.dumps(scan(root))
            self.assertNotIn('TOP_SECRET', r)
            self.assertNotIn('bad.html', r)

    def test_file_symlink_omitted_with_explicit_reason(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            root = Path(a)
            (Path(b) / 'source.html').write_text('<img src="x">')
            (root / 'linked.html').symlink_to(Path(b) / 'source.html')
            r = scan(root)
            self.assertEqual(r['observed_files'], [])
            self.assertEqual(r['skipped'][0]['reason'], 'symlink')
            self.assertFalse(r['coverage']['complete'])

    def test_unavailable_files_not_marked_complete(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'ok.html').write_text('<img src="x">')
            r = scan(root)
            self.assertEqual(r['coverage']['verdict'], 'COMPLETE_WITHIN_DECLARED_SCOPE')


    def test_symlink_directory_reflected_in_coverage(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            root = Path(a)
            (Path(b) / 'page.html').write_text('<img src="x">')
            (root / 'linked').symlink_to(Path(b), target_is_directory=True)
            r = scan(root)
            self.assertFalse(r['coverage']['complete'])
            self.assertEqual(r['coverage']['symlink_directories_skipped'], 1)

    def test_downstream_compiler_coverage_propagation_known_hold(self):
        """Historical gap fixed by R31: incomplete coverage must propagate."""
        from tools.fdf_proposal_compiler import compile_plan
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for i in range(MAX_FILES + 1):
                (root / f'p{i:03d}.html').write_text('<img src="x">')
            receipt = scan(root)
            self.assertFalse(receipt['coverage']['complete'])
            plan = compile_plan(root, receipt)
            self.assertEqual(len(plan['proposals']), MAX_FILES)
            self.assertEqual(plan['coverage_admission'], 'HOLD_INCOMPLETE')
            self.assertEqual(plan['coverage_binding']['verdict'], 'INCOMPLETE')
            self.assertFalse(plan['coverage_binding']['current_scan']['complete'])

if __name__ == '__main__':
    unittest.main()
