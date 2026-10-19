"""Run original pinned UAC v0.2 tests in the existing FDF source CI."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1] / "distribution/uac-v0.2"

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, BASE / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

Adoption = load("tests/test_fdf_adopt.py", "uac006_original_adoption").Adoption
Kernel = load("tests/test_fdf_kernel.py", "uac006_original_kernel").Kernel

class UAC006OriginalSourceParity(unittest.TestCase):
    def test_all_fourteen_original_files_match_manifest(self):
        index = json.loads((BASE / "FABRICA_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(index.get("schema"), "fdf.source-manifest/0.2")
        entries = index.get("files", [])
        self.assertEqual(len(entries), 14)
        self.assertEqual(len({x["path"] for x in entries}), 14)
        for e in entries:
            path = BASE / e["path"]
            raw = path.read_bytes()
            self.assertEqual(len(raw), e["bytes"], e["path"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), e["sha256"], e["path"])
