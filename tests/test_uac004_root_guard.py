"""Expose research-only UAC-004 guard tests to existing source CI discovery."""
import importlib.util
from pathlib import Path
source = Path(__file__).resolve().parents[1] / 'research/uac004/tests/test_fdf_root_guard.py'
spec = importlib.util.spec_from_file_location('uac004_root_guard_tests', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
RootGuard = module.RootGuard
