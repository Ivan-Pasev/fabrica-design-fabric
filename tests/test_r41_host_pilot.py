"""R41 real-host pilot artifact integrity; NOT a witnessed real IDE test."""
import copy
import hashlib
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from tools.fdf_host_pilot import capture, admit, _digest, _png_dimensions
from tools.fdf_proposal_compiler import stable_json

SHA = "c760133df05e9b8e65366e4d641013f11b0f70de"


def mock_png(w, h, payload=b"A"):
    # Structurally framed PNG with CRCs; image semantics still not verified.
    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data +
                struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))
    header = struct.pack(">II", w, h) + b"\x08\x06\x00\x00\x00"
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) +
            chunk(b"IDAT", zlib.compress(payload)) + chunk(b"IEND", b""))

class PilotEvidence(unittest.TestCase):
    def setUp(self):
        a = tempfile.TemporaryDirectory()
        b = tempfile.TemporaryDirectory()
        self.addCleanup(a.cleanup)
        self.addCleanup(b.cleanup)
        self.project, self.evidence = Path(a.name), Path(b.name)
        (self.project / "AGENTS.md").write_text("local host agent constraints", encoding="utf-8")
        (self.project / "home.tsx").write_text('<img data-note="alt=spoof">', encoding="utf-8")
        self.baseline = capture(self.project, SHA)
        (self.evidence / "baseline.json").write_text(json.dumps(self.baseline), encoding="utf-8")
        (self.project / "home.tsx").write_text('<img alt="title">', encoding="utf-8")
        self.manifest = {
            "schema": "fdf.host.pilot-manifest/0.1",
            "fdf_source_commit": SHA,
            "baseline_receipt": "baseline.json",
            "screenshots": {},
            "checks": {},
            "rollback": {},
        }
        for key, size, extra in (
            ("baseline_desktop", (1280, 800), b"A"),
            ("after_desktop", (1280, 800), b"B"),
            ("baseline_mobile", (390, 800), b"A"),
            ("after_mobile", (390, 800), b"B"),
        ):
            self.manifest["screenshots"][key] = self.artifact(key + ".png", mock_png(*size, extra))
        for key in ("build", "keyboard"):
            entry = self.artifact(key + ".log", (key + " reported PASS").encode())
            self.manifest["checks"][key] = dict(entry, reported_status="PASS")
        self.manifest["rollback"] = self.artifact("rollback.md", b"Restore baseline through host git")

    def artifact(self, name, contents):
        (self.evidence / name).write_bytes(contents)
        return {"path": name, "sha256": _digest(contents)}

    def check(self):
        (self.evidence / "manifest.json").write_text(json.dumps(self.manifest))
        return admit(self.project, SHA, self.evidence, "manifest.json")

    def test_positive_fixture_is_only_artifact_integrity(self):
        r = self.check()
        self.assertEqual(r["admission"], "ARTIFACT_BYTES_AND_POST_SOURCE_BOUNDED_CHECK_COMPLETE")
        self.assertEqual(r["changed_ui_source_paths"], ["home.tsx"])
        self.assertEqual(r["visual_design_quality"], "NOT_EVALUATED")
        self.assertEqual(r["host_test_execution"], "NOT_REPLAYED")
        self.assertEqual(r["real_ide_witness"], "NOT_VERIFIED")
        self.assertEqual(r["independent_approval"], "HOLD")
        self.assertEqual(r["release"], "HOLD")

    def test_capture_has_no_authority(self):
        self.assertFalse(self.baseline["owner_authorized"])
        self.assertFalse(self.baseline["host_master_witnessed"])
        self.assertEqual(self.baseline["tests_executed"], [])
        self.assertEqual(self.baseline["release"], "HOLD")

    def test_no_source_change_denied(self):
        (self.project / "home.tsx").write_text('<img data-note="alt=spoof">')
        with self.assertRaisesRegex(ValueError, "no UI source difference"):
            self.check()

    def test_policy_drift_denied(self):
        (self.project / "AGENTS.md").write_text("policy updated")
        with self.assertRaisesRegex(ValueError, "host policy changed"):
            self.check()

    def test_tampered_baseline_denied(self):
        x = copy.deepcopy(self.baseline)
        x["observed_files"] = []
        (self.evidence / "baseline.json").write_text(json.dumps(x))
        with self.assertRaisesRegex(ValueError, "baseline integrity"):
            self.check()

    def test_forged_baseline_authorization_denied(self):
        x = copy.deepcopy(self.baseline)
        x["owner_authorized"] = True
        x.pop("receipt_sha256")
        x["receipt_sha256"] = _digest(stable_json(x))
        (self.evidence / "baseline.json").write_text(json.dumps(x))
        with self.assertRaisesRegex(ValueError, "cannot assert authority"):
            self.check()

    def test_invalid_png_denied(self):
        self.manifest["screenshots"]["after_desktop"] = self.artifact("not.png", b"not a screenshot")
        with self.assertRaisesRegex(ValueError, "PNG"):
            self.check()

    def test_changed_png_size_denied(self):
        self.manifest["screenshots"]["after_mobile"] = self.artifact("bad.png", mock_png(400, 800, b"B"))
        with self.assertRaisesRegex(ValueError, "dimensions differ"):
            self.check()

    def test_identical_pngs_denied(self):
        for size in ("desktop", "mobile"):
            self.manifest["screenshots"]["after_" + size] = self.manifest["screenshots"]["baseline_" + size]
        with self.assertRaisesRegex(ValueError, "no visual artifact difference"):
            self.check()

    def test_screenshot_hash_mismatch_denied(self):
        self.manifest["screenshots"]["after_mobile"]["sha256"] = "f"*64
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.check()

    def test_check_must_be_reported_pass(self):
        self.manifest["checks"]["build"]["reported_status"] = "UNKNOWN"
        with self.assertRaisesRegex(ValueError, "non-PASS"):
            self.check()

    def test_rollback_required(self):
        del self.manifest["rollback"]
        with self.assertRaisesRegex(ValueError, "manifest keys"):
            self.check()

    def test_traversal_denied(self):
        self.manifest["rollback"]["path"] = "../outside.md"
        with self.assertRaisesRegex(ValueError, "traversal"):
            self.check()

    def test_symlink_outside_denied(self):
        with tempfile.TemporaryDirectory() as td:
            outside = Path(td)/"outside.md"
            outside.write_text("host secret")
            (self.evidence/"alias.md").symlink_to(outside)
            self.manifest["rollback"]["path"] = "alias.md"
            self.manifest["rollback"]["sha256"] = _digest(outside.read_bytes())
            with self.assertRaisesRegex(ValueError, "symlink"):
                self.check()

    def test_oversized_log_denied(self):
        self.manifest["checks"]["build"] = dict(
            self.artifact("big.log", b"X"*(10*1024*1024+1)),
            reported_status="PASS")
        with self.assertRaisesRegex(ValueError, "oversized"):
            self.check()

    def test_sha_mismatch_denied(self):
        self.manifest["fdf_source_commit"] = "1"*40
        with self.assertRaisesRegex(ValueError, "source mismatch"):
            self.check()

    def test_missing_scans_denied(self):
        (self.project / "home.tsx").unlink()
        with self.assertRaisesRegex(ValueError, "intake incomplete"):
            self.check()

    def test_bad_png_crc_denied(self):
        corrupted = bytearray(mock_png(1280, 800, b"changed"))
        corrupted[29] ^= 0x20
        self.manifest["screenshots"]["after_desktop"] = self.artifact("bad-crc.png", bytes(corrupted))
        with self.assertRaisesRegex(ValueError, "CRC mismatch"):
            self.check()

    def test_truncated_png_end_denied(self):
        broken = mock_png(1280, 800)[:-12]
        self.manifest["screenshots"]["after_desktop"] = self.artifact("cut.png", broken)
        with self.assertRaisesRegex(ValueError, "final IEND"):
            self.check()

    def test_screen_bounds_reject_tiny_header(self):
        with self.assertRaisesRegex(ValueError, "outside bounded"):
            _png_dimensions(mock_png(10, 10))

if __name__ == "__main__":
    unittest.main()
