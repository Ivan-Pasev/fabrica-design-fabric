"""Controlled fixtures for UAC-002 minimal repo preview, no caller writes."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
S=Path(__file__).resolve().parents[1]/"tools"/"fdf_uac_readonly.py"
spec=importlib.util.spec_from_file_location("fdf_uac",S)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class UAC(unittest.TestCase):
 def test_empty_proposes_advisory_kernel(self):
  with tempfile.TemporaryDirectory() as root:
   result=mod.inspect(root)
   self.assertEqual(result["mode"],"SCAFFOLD_ADVISORY_KERNEL")
   self.assertFalse(result["files_written"])
   self.assertEqual(result["release"],"HOLD")
 def test_existing_policy_keeps_authority(self):
  with tempfile.TemporaryDirectory() as root:
   path=Path(root)/"AGENTS.md";path.write_text("SECRET DO NOT SHARE")
   result=mod.inspect(root)
   self.assertEqual(result["mode"],"AUGMENT_EXISTING_UNVERIFIED")
   self.assertNotIn("SECRET",str(result))
   self.assertEqual(path.read_text(),"SECRET DO NOT SHARE")
 def test_ui_selects_accessibility(self):
  with tempfile.TemporaryDirectory() as root:
   (Path(root)/"index.html").write_text("<h1>site</h1>")
   result=mod.inspect(root)
   self.assertIn("fdf-accessibility-review",result["selected_first_party_skills"])
 def test_reject_symlink_policy(self):
  with tempfile.TemporaryDirectory() as root:
   (Path(root)/"AGENTS.md").symlink_to("missing")
   with self.assertRaisesRegex(ValueError,"symlink"):mod.inspect(root)
if __name__=="__main__":unittest.main()
