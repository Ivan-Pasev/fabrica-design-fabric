"""UAC-008: ensure GitHub has the byte-identical UAC-007 source and run its tests."""
import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "distribution/uac-v0.2"

class UAC008SourceAndTests(unittest.TestCase):
    def test_all_twenty_archive_items_match_package_manifest(self):
        index = json.loads((BASE / "UAC007_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(index.get("schema"), "fdf.uac007.package/0.1")
        entries = index["files"]
        self.assertEqual(len(entries), 19)
        for relative, expected in entries.items():
            data = (BASE / relative).read_bytes()
            self.assertEqual(len(data), expected["bytes"], relative)
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected["sha256"], relative)

    def test_exact_imported_uac007_transaction_suite(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join([str(BASE), str(BASE / "tools"), env.get("PYTHONPATH", "")])
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_fdf_safe.py", "-v"],
            cwd=BASE, env=env, text=True, capture_output=True, timeout=90,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("Ran 13 tests", proc.stderr)
        self.assertIn("OK", proc.stderr)

if __name__ == "__main__": unittest.main()
