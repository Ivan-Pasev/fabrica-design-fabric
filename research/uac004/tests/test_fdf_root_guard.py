import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('fdf_root_guard',ROOT/'tools'/'fdf_root_guard.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

@unittest.skipUnless(os.name=='posix' and hasattr(os,'O_NOFOLLOW'),'POSIX no-follow required')
class RootGuard(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        self.old=b'Existing owner laws\r\nRoot authority\n'
        (self.root/'AGENTS.md').write_bytes(self.old)
    def test_append_verify_recovery_exact_bytes(self):
        tail=b'\n<!-- reviewed advisory -->\n'
        x=m.append_guarded(self.root,'AGENTS.md',m.sha(self.old),tail)
        self.assertEqual(x['release'],'HOLD')
        self.assertEqual((self.root/'AGENTS.md').read_bytes(),self.old+tail)
        rec=(self.root/'.fabrica/UAC004_AGENTS.md.journal.json').read_text()
        self.assertNotIn('Existing owner laws',rec)
        self.assertEqual(m.inspect_recovery(self.root,'AGENTS.md')['recovery_status'],'APPENDED_INTACT')
        self.assertEqual(m.inspect_recovery(self.root,'AGENTS.md',restore=True)['recovery_status'],'RESTORED_AND_JOURNAL_CLEARED')
        self.assertEqual((self.root/'AGENTS.md').read_bytes(),self.old)
    def test_refuse_modified_original(self):
        with self.assertRaisesRegex(ValueError,'SHA drift'):
            m.append_guarded(self.root,'AGENTS.md','0'*64,b'append')
        self.assertFalse((self.root/'.fabrica').exists())
    def test_refuse_symlink_target(self):
        (self.root/'AGENTS.md').unlink();(self.root/'AGENTS.md').symlink_to('other-policy')
        with self.assertRaises(OSError):m.append_guarded(self.root,'AGENTS.md',m.sha(self.old),b'abc')
    def test_refuse_modified_after_append(self):
        m.append_guarded(self.root,'AGENTS.md',m.sha(self.old),b' FDF')
        (self.root/'AGENTS.md').write_bytes(self.old+b' FDF'+b' OWNER CHANGE')
        self.assertEqual(m.inspect_recovery(self.root,'AGENTS.md')['recovery_status'],'HOLD_POLICY_MODIFIED_OR_PARTIAL')
        with self.assertRaisesRegex(ValueError,'do not truncate'):
            m.inspect_recovery(self.root,'AGENTS.md',restore=True)
    def test_prepared_without_mutation(self):
        fd=m.root_fd(self.root)
        try:
            jfd=m.journal_dir_fd(fd)
            try:m.make_journal(jfd,'AGENTS.md',{'schema':'fdf.uac004.journal/0.1','target':'AGENTS.md','before':m.sha(self.old),'after':m.sha(self.old+b' xyz'),'tail':m.sha(b' xyz'),'before_length':len(self.old)})
            finally:os.close(jfd)
        finally:os.close(fd)
        self.assertEqual(m.inspect_recovery(self.root,'AGENTS.md')['recovery_status'],'PREPARED_NOT_APPLIED')
        m.inspect_recovery(self.root,'AGENTS.md',restore=True)
        self.assertEqual((self.root/'AGENTS.md').read_bytes(),self.old)
    def test_duplicate_attempt_hold_with_journal(self):
        m.append_guarded(self.root,'AGENTS.md',m.sha(self.old),b' first')
        with self.assertRaises(FileExistsError):m.append_guarded(self.root,'AGENTS.md',m.sha(self.old+b' first'),b' second')
    def test_allowlisted_root_only(self):
        with self.assertRaisesRegex(ValueError,'not allowlisted'):
            m.append_guarded(self.root,'CLAUDE.md','0'*64,b'x')
    def test_root_symlink_not_followed(self):
        linked=self.root.parent/'link-uac004-does-not-exist'
        if linked.exists():linked.unlink()
        linked.symlink_to(self.root,target_is_directory=True)
        self.addCleanup(lambda: linked.unlink(missing_ok=True))
        with self.assertRaises(OSError):m.append_guarded(linked,'AGENTS.md',m.sha(self.old),b'x')

if __name__=='__main__':unittest.main()
