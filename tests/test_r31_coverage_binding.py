"""R31 coverage-bound ProposalDNA: source, coverage, permission and negative tests."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.fdf_workspace_probe import scan, MAX_FILES, MAX_DEPTH
from tools.fdf_proposal_compiler import compile_plan


class CoverageBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'page.tsx').write_text('<img src="portrait.png">', encoding='utf-8')
        self.receipt = scan(self.root)

    def test_complete_scoped_coverage_propagated(self):
        p = compile_plan(self.root, self.receipt)
        b = p['coverage_binding']
        self.assertEqual(p['schema'], 'fdf.kbi.proposaldna/0.2')
        self.assertEqual(p['coverage_admission'], 'PASS_SCOPED')
        self.assertEqual(b['verdict'], 'COMPLETE_WITHIN_DECLARED_SCOPE')
        self.assertTrue(b['scope_limited'])
        self.assertFalse(b['complete_project_audit'])
        self.assertEqual(b['receipt_coverage_sha256'], b['fresh_scan_sha256'])
        self.assertFalse(p['mutations_performed'])
        self.assertTrue(p['owner_approval_required'])
        self.assertIsNone(p['proposals'][0]['executable_patch'])
        self.assertFalse(p['proposals'][0]['owner_authorized'])

    def test_stable_output_on_same_project(self):
        self.assertEqual(compile_plan(self.root,self.receipt), compile_plan(self.root,self.receipt))

    def test_changed_coverage_denied(self):
        x = copy.deepcopy(self.receipt)
        x['coverage']['complete'] = False
        with self.assertRaisesRegex(ValueError, 'coverage'):compile_plan(self.root,x)

    def test_forged_complete_on_incomplete_denied(self):
        for i in range(MAX_FILES + 1):
            (self.root / f'a{i:03}.tsx').write_text('<img src="x">')
        x = scan(self.root)
        self.assertEqual(x['coverage']['verdict'], 'INCOMPLETE')
        x['coverage']['complete'] = True
        x['coverage']['verdict'] = 'COMPLETE_WITHIN_DECLARED_SCOPE'
        with self.assertRaisesRegex(ValueError, 'coverage'):compile_plan(self.root,x)

    def test_coverage_added_unknown_keys_denied(self):
        x=copy.deepcopy(self.receipt);x['coverage']['privileged_skip_exemption']=True
        with self.assertRaisesRegex(ValueError, 'coverage'):compile_plan(self.root,x)

    def test_skipped_file_evidence_tamper_denied(self):
        x=copy.deepcopy(self.receipt);x['skipped']=[{'path':'page.tsx','reason':'file_cap'}]
        with self.assertRaisesRegex(ValueError, 'skipped'):compile_plan(self.root,x)

    def test_new_coverage_missing_skipped_denied(self):
        x=copy.deepcopy(self.receipt);del x['skipped']
        with self.assertRaisesRegex(ValueError, 'skipped'):compile_plan(self.root,x)

    def test_legacy_complete_stays_unknown(self):
        x=copy.deepcopy(self.receipt);del x['coverage']
        p=compile_plan(self.root,x)
        self.assertEqual(p['coverage_admission'],'HOLD_UNKNOWN_LEGACY')
        self.assertEqual(p['coverage_binding']['verdict'],'UNKNOWN_LEGACY')
        self.assertIsNone(p['coverage_binding']['receipt_coverage_sha256'])
        self.assertTrue(p['coverage_binding']['current_scan']['complete'])

    def test_legacy_incomplete_is_known_hold(self):
        for i in range(MAX_FILES+1):
            (self.root/f'z{i:03}.tsx').write_text('<img src="x">')
        x=scan(self.root); del x['coverage']
        p=compile_plan(self.root,x)
        self.assertEqual(p['coverage_admission'],'HOLD_INCOMPLETE')
        self.assertFalse(p['coverage_binding']['current_scan']['complete'])

    def test_file_cap_still_visible(self):
        for i in range(MAX_FILES+1):
            (self.root/f'a{i:03}.html').write_text('<img src="x">')
        p=compile_plan(self.root,scan(self.root))
        self.assertTrue(p['coverage_binding']['current_scan']['file_cap_reached'])
        self.assertEqual(p['coverage_admission'],'HOLD_INCOMPLETE')

    def test_oversized_skipped_file_visible(self):
        (self.root/'oversized.css').write_text('x'*65537)
        p=compile_plan(self.root,scan(self.root))
        self.assertEqual(p['coverage_admission'],'HOLD_INCOMPLETE')
        self.assertGreaterEqual(p['coverage_binding']['current_scan']['skipped_files_recorded'],1)

    def test_symlink_directory_visible(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root/'alias').symlink_to(outside, target_is_directory=True)
            p=compile_plan(self.root,scan(self.root))
            self.assertEqual(p['coverage_admission'],'HOLD_INCOMPLETE')
            self.assertEqual(p['coverage_binding']['current_scan']['symlink_directories_skipped'],1)

    def test_depth_limit_visible(self):
        x=self.root
        for i in range(MAX_DEPTH+1):
            x=x/f'd{i}';x.mkdir()
        (x/'nested.html').write_text('<img>')
        p=compile_plan(self.root,scan(self.root))
        self.assertEqual(p['coverage_admission'],'HOLD_INCOMPLETE')
        self.assertTrue(p['coverage_binding']['current_scan']['depth_cap_reached'])

    def test_missing_coverage_is_not_a_bypass_for_owner_gate(self):
        x=copy.deepcopy(self.receipt); del x['coverage']; x['approval_required_for_mutation']=False
        with self.assertRaisesRegex(ValueError,'authorization'):compile_plan(self.root,x)

    def test_scanner_tests_claim_denied(self):
        x=copy.deepcopy(self.receipt);x['tests_executed']=['production_build_success']
        with self.assertRaisesRegex(ValueError,'executed tests'):compile_plan(self.root,x)

    def test_current_source_staleness_still_denied(self):
        (self.root/'page.tsx').write_text('<img src="different">')
        with self.assertRaisesRegex(ValueError,'stale'):compile_plan(self.root,self.receipt)

    def test_cli_live_outputs_coverage_and_no_write(self):
        prior = (self.root/'page.tsx').read_bytes()
        script=Path(__file__).resolve().parents[1]/'tools'/'fdf_proposal_compiler.py'
        done=subprocess.run([sys.executable,str(script),'--project',str(self.root),'--live'],
                            capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(done.stdout)['coverage_admission'],'PASS_SCOPED')
        self.assertEqual(prior,(self.root/'page.tsx').read_bytes())

    def test_cli_observations_legacy(self):
        x=copy.deepcopy(self.receipt);del x['coverage']
        path=self.root/'receipt.json';path.write_text(json.dumps(x))
        script=Path(__file__).resolve().parents[1]/'tools'/'fdf_proposal_compiler.py'
        done=subprocess.run([sys.executable,str(script),'--project',str(self.root),
                             '--observations',str(path)],capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(done.stdout)['coverage_admission'],'HOLD_UNKNOWN_LEGACY')

    def test_no_private_files_in_proposals(self):
        (self.root/'.env').write_text('R31_DO_NOT_ECHO_SECRET')
        p=compile_plan(self.root,self.receipt)
        self.assertNotIn('R31_DO_NOT_ECHO_SECRET',json.dumps(p))


if __name__=='__main__': unittest.main()
