"""R33 independently sourced R32 defects, plus negative/control regressions."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.fdf_workspace_probe import scan
from tools.fdf_proposal_compiler import compile_plan

class R33ScannerRegression(unittest.TestCase):
    def fixture(self, filename, content):
        t=tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup)
        p=Path(t.name); (p/filename).write_text(content, encoding='utf-8')
        return p

    def test_r32_f01_data_alt_does_not_mask_real_alt(self):
        p=self.fixture('index.html','<img data-alt="tooltip" src="a.png">')
        o=scan(p);self.assertEqual([x['rule'] for x in o['candidate_changes']],['img_missing_alt'])
        self.assertTrue(o['coverage']['complete'])
        self.assertEqual(compile_plan(p,o)['coverage_admission'],'PASS_SCOPED')

    def test_real_alt_is_preserved(self):
        p=self.fixture('index.html','<img alt="Actual name" data-alt="other" src="a.png">')
        self.assertEqual(scan(p)['candidate_changes'],[])

    def test_colon_alt_and_hyphen_alt_are_not_alt(self):
        p=self.fixture('index.html','<img aria-alt="other"><img :alt="dynamic">')
        self.assertEqual(len(scan(p)['candidate_changes']),2)

    def test_icon_button_data_aria_label_does_not_mask_accessible_name(self):
        p=self.fixture('index.html','<button data-aria-label="false"><svg></svg></button>')
        self.assertEqual([x['rule'] for x in scan(p)['candidate_changes']], ['icon_button_name'])

    def test_real_aria_label_still_present(self):
        p=self.fixture('index.html','<button aria-label="Open menu"><svg></svg></button>')
        self.assertEqual(scan(p)['candidate_changes'],[])

    def test_r32_f02_unrelated_css_none_after_media_does_not_mask(self):
        p=self.fixture('motion.css','.hero{animation: spin 3s infinite;} @media (prefers-reduced-motion: reduce) {.body{color:red}} .other{animation:none}')
        self.assertEqual([x['rule'] for x in scan(p)['candidate_changes']],['reduced_motion_equivalence'])

    def test_reduction_inside_media_still_accepted(self):
        p=self.fixture('motion.css','.hero{animation: spin 3s infinite;} @media (prefers-reduced-motion: reduce) { .hero{animation:none} }')
        self.assertEqual(scan(p)['candidate_changes'],[])

    def test_reduction_before_media_not_accepted(self):
        p=self.fixture('motion.css','.other{animation:none} .hero{animation:spin 3s} @media(prefers-reduced-motion:reduce){.hero{color:blue}}')
        self.assertEqual(scan(p)['candidate_changes'][0]['rule'],'reduced_motion_equivalence')

    def test_comment_only_reduction_not_accepted(self):
        p=self.fixture('motion.css','.hero{animation:spin 3s} @media(prefers-reduced-motion:reduce){/* .hero{animation:none} */color:red}')
        self.assertEqual(scan(p)['candidate_changes'][0]['rule'],'reduced_motion_equivalence')

    def test_r32_f03_simulated_silent_unvisited_dir_forces_hold(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'nested').mkdir();(root/'nested/lost.html').write_text('<img src="x">')
            def lost_walk(top, topdown=True, followlinks=False, onerror=None):
                yield str(root), ['nested'], []
            with patch('tools.fdf_workspace_probe.os.walk',side_effect=lost_walk):
                observed=scan(root)
                self.assertFalse(observed['coverage']['complete'])
                self.assertEqual(observed['coverage']['unvisited_directories'],1)
                self.assertEqual(compile_plan(root,observed)['coverage_admission'],'HOLD_INCOMPLETE')

    def test_onerror_callback_forces_hold(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            def failing_walk(top, topdown=True, followlinks=False, onerror=None):
                onerror(PermissionError('access denied'))
                yield str(root), [], []
            with patch('tools.fdf_workspace_probe.os.walk',side_effect=failing_walk):
                observed=scan(root)
            self.assertEqual(observed['coverage']['walk_errors'],1)
            self.assertEqual(observed['coverage']['walk_error_types'],['PermissionError'])
            self.assertFalse(observed['coverage']['complete'])
            self.assertNotIn('access denied',json.dumps(observed))

    def test_verified_subdir_complete(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'nested').mkdir();(p/'nested/x.html').write_text('<img src="x">')
            r=scan(p);self.assertTrue(r['coverage']['complete']);self.assertEqual(r['coverage']['unvisited_directories'],0)

    def test_walker_gap_freshness_still_detected(self):
        p=self.fixture('index.html','<img src="a">')
        source=scan(p)
        changed=source.copy();changed['coverage']=dict(source['coverage']);changed['coverage']['unvisited_directories']=1
        with self.assertRaisesRegex(ValueError,'coverage'):compile_plan(p,changed)

    def test_no_writes_to_caller(self):
        p=self.fixture('index.html','<img data-alt="x">');before=(p/'index.html').read_bytes()
        result=compile_plan(p,scan(p));self.assertEqual((p/'index.html').read_bytes(),before)
        self.assertTrue(result['owner_approval_required']);self.assertFalse(result['mutations_performed'])
        self.assertTrue(all(z['executable_patch'] is None and not z['owner_authorized'] for z in result['proposals']))

if __name__=='__main__': unittest.main()
