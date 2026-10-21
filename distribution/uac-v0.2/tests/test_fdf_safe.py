"""Adversarial and interrupted transaction tests for cooperative-only UAC-007."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import fdf_safe as m
class SafeTransaction(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'AGENTS.md').write_bytes(b'Host law\r\nDo not change.\r\n')
        (self.root/'GEMINI.md').write_bytes(b'Existing Gemini rules\n')
        self.before=[(p,(self.root/p).read_bytes()) for p in ('AGENTS.md','GEMINI.md')]
        self.platforms=['codex','cursor']
    def plan(self):return m.planned(self.root,self.platforms)[0]
    def apply(self, fault=None):
        return m.install(self.root,self.platforms,self.plan()['transaction_sha256'],trusted_single_writer=True,fault_after=fault)
    def test_no_writes_during_plan(self):
        x=self.plan();self.assertFalse((self.root/'.fabrica').exists());self.assertEqual(x['release'],'HOLD')
    def test_exact_gate(self):
        with self.assertRaisesRegex(ValueError,'stale plan'):
            m.install(self.root,self.platforms,'x',trusted_single_writer=True)
    def test_requires_single_writer(self):
        with self.assertRaisesRegex(ValueError,'trusted-single-writer'):
            m.install(self.root,self.platforms,self.plan()['transaction_sha256'])
    def test_existing_policy_byte_identity_and_rollback(self):
        sha=self.plan()['transaction_sha256'];self.apply();self.assertEqual(m.status(self.root)['verdict'],'COMPLETE_HASHES_MATCH')
        m.rollback(self.root,sha,trusted_single_writer=True)
        for name,old in self.before:self.assertEqual((self.root/name).read_bytes(),old)
        self.assertFalse((self.root/'.fabrica/UAC007_TRANSACTION.json').exists())
    def test_crash_one_file_recoverable(self):
        sha=self.plan()['transaction_sha256']
        with self.assertRaisesRegex(RuntimeError,'INJECTED_CRASH'):self.apply(fault=1)
        self.assertEqual(m.status(self.root)['verdict'],'INTERRUPTED_RECOVERABLE')
        m.rollback(self.root,sha,trusted_single_writer=True)
        self.assertFalse((self.root/'.fabrica').exists())
    def test_crash_mid_files_recoverable(self):
        sha=self.plan()['transaction_sha256']
        with self.assertRaisesRegex(RuntimeError,'INJECTED_CRASH'):self.apply(fault=4)
        m.rollback(self.root,sha,trusted_single_writer=True)
        for name,old in self.before:self.assertEqual((self.root/name).read_bytes(),old)
    def test_owner_drift_blocks_rollback(self):
        sha=self.plan()['transaction_sha256'];self.apply()
        a=self.plan_file();a.write_text(a.read_text()+'OWNER EDIT')
        with self.assertRaisesRegex(ValueError,'owner drift'):m.rollback(self.root,sha,trusted_single_writer=True)
        self.assertTrue(a.exists())
    def plan_file(self):return self.root/self.plan_actions()[0]['path']
    def plan_actions(self):return m.read_journal(self.root)['files']
    def test_symlink_generated_path_hold(self):
        outside=self.root/'outside';outside.mkdir()
        (self.root/'.cursor').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'symlink'):
            self.plan()
    def test_no_existing_root_hooks_ever(self):
        self.assertNotIn('root_hooks',self.plan())
        for name,old in self.before:self.assertEqual((self.root/name).read_bytes(),old)
    def test_manifest_drift_blocks_rollback(self):
        sha=self.plan()['transaction_sha256'];self.apply()
        (self.root/m.MANIFEST).write_text('{"plan_sha256":"WRONG"}')
        with self.assertRaisesRegex(ValueError,'owner drift'):m.rollback(self.root,sha,trusted_single_writer=True)
    def test_replay_requires_recovery(self):
        self.apply()
        with self.assertRaisesRegex(ValueError,'existing managed path collision|existing transaction'):
            self.plan()
    def test_preserve_preexisting_empty_directories(self):
        (self.root/'.cursor').mkdir()
        sha=self.plan()['transaction_sha256']
        self.apply()
        m.rollback(self.root,sha,trusted_single_writer=True)
        self.assertTrue((self.root/'.cursor').is_dir())
    def test_no_automatic_human_ide_claim(self):
        self.apply();x=m.status(self.root);self.assertFalse(x['actual_ide_verified']);self.assertEqual(x['release'],'HOLD')
if __name__=='__main__':unittest.main()
