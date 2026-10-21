"""Windows-native, non-IDE replay of UAC-007; skip symlink privilege-dependent test.

This is NOT a race/NTFS junction qualification nor proof of host instruction loading.
"""
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[2] / "distribution/uac-v0.2"
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tools"))
spec = importlib.util.spec_from_file_location("uac008_original_safe_tests", BASE / "tests/test_fdf_safe.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

if os.name != "nt":
    print("HOLD: Windows-native qualification must execute on Windows", file=sys.stderr)
    raise SystemExit(2)

methods = [name for name in unittest.defaultTestLoader.getTestCaseNames(module.SafeTransaction)
           if name != "test_symlink_generated_path_hold"]
assert len(methods) == 12, "unexpected original transaction-test inventory"
suite = unittest.TestSuite(module.SafeTransaction(name) for name in methods)
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
