"""Expose UAC-005 isolated source-promotion tests to existing GitHub CI."""
import importlib.util
from pathlib import Path
s = Path(__file__).resolve().parents[1] / 'research/uac005/tests/test_uac005_promote.py'
x = importlib.util.spec_from_file_location('uac005_source_import_tests', s)
module = importlib.util.module_from_spec(x)
x.loader.exec_module(module)
Promoter = module.Promoter
