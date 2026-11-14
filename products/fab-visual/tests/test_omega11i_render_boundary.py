"""Ω11I source-pinned renderer boundary, negative controls and nonadmission."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT=Path(__file__).resolve().parent.parent/"scripts"/"omega11i-render-boundary.py"
spec=importlib.util.spec_from_file_location("omega11i_source_audit",SCRIPT)
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)

RAPTOR=(b"const D={};function f(){requestAnimationFrame(tick);requestAnimationFrame(tick);"
        b"new IntersectionObserver(cb);setTimeout(cb,300);glLayer({camera:D.camera});"
        b"stage.style.transform='translate(0px)';}")
TURN=(b"const LIVE = 'a';T.build();const started=Date.now();"
      b"function f(){requestAnimationFrame(tick);requestAnimationFrame(tick);"
      b"new IntersectionObserver(cb);performance.now();performance.now();"
      b"controller.set({table:1,lift:1,time:0});}")

def fake_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

class SourceCoverageProof(unittest.TestCase):
    def test_raptor_source_api_inventory(self):
        with patch.dict(A.SOURCES,{"raptor":("r.js",fake_blob(RAPTOR))},clear=True):
            a=A.analyze_source("raptor",RAPTOR)
            self.assertEqual(a["source_apis"]["setTimeout"]["count"],1)
            self.assertEqual(a["source_apis"]["setTimeout"]["coverage_class"],"UNCONTROLLED_NATIVE_TIMER")
            self.assertEqual(a["actual_gpu_compositor_present_event"],"NOT_IDENTIFIED")
            self.assertEqual(a["renderer_frame_state_binding"],"NOT_ADMITTED")
    def test_turning_generator_and_clock_inventory(self):
        with patch.dict(A.SOURCES,{"turning":("t.mjs",fake_blob(TURN))},clear=True):
            a=A.analyze_source("turning",TURN)
            self.assertEqual(a["source_apis"]["Date.now"]["count"],1)
            self.assertEqual(a["source_apis"]["performance.now"]["count"],2)
            self.assertEqual(a["source_apis"]["controller.set"]["count"],1)
            self.assertEqual(a["real_part_mesh_transform_camera_depth"],"NOT_RUN")
    def test_wrong_original_git_blob_rejected(self):
        with self.assertRaises(ValueError):A.analyze_source("raptor",b"fake source")
    def test_missing_source_timer_anchor_rejected(self):
        wrong=RAPTOR.replace(b"setTimeout(",b"otherTimer(")
        with patch.dict(A.SOURCES,{"raptor":("r.js",fake_blob(wrong))},clear=True):
            with self.assertRaises(ValueError):A.analyze_source("raptor",wrong)
    def test_missing_turning_controller_rejected(self):
        wrong=TURN.replace(b"controller.set",b"unknown.apply")
        with patch.dict(A.SOURCES,{"turning":("t.mjs",fake_blob(wrong))},clear=True):
            with self.assertRaises(ValueError):A.analyze_source("turning",wrong)
    def test_static_source_not_comprehensive_semantics(self):
        self.assertEqual(A.SCHEDULE["getContext"],"RENDERER_CONTEXT_NOT_PRESENT_WITNESS")
        self.assertEqual(A.SCHEDULE["setTimeout"],"UNCONTROLLED_NATIVE_TIMER")
        self.assertEqual(A.SCHEDULE["Date.now"],"UNCONTROLLED_NATIVE_OR_GENERATOR_DATE")
    def test_no_witness_refused(self):
        self.assertEqual(A.frame_gate(None),"FAIL_MISSING_WITNESS")
    def test_wrong_source_attestation_rejected(self):
        self.assertEqual(A.frame_gate({"original_source_pin":"0"*40,"scene":"raptor",
                       "observation_grade":"GPU_PRESENTED"}),"FAIL_SOURCE_PROVENANCE")
    def test_wrong_scene_rejected(self):
        self.assertEqual(A.frame_gate({"original_source_pin":A.PIN,"scene":"fabricated",
                       "observation_grade":"GPU_PRESENTED"}),"FAIL_SCENE")
    def test_screenshot_is_not_gpu_present(self):
        self.assertEqual(A.frame_gate({"original_source_pin":A.PIN,"scene":"turning",
                       "observation_grade":"SCREENSHOT_SHA"}),"NOT_ADMITTED_STATE_OR_CAPTURE_IS_NOT_PRESENT")
    def test_controller_set_is_not_gpu_present(self):
        self.assertEqual(A.frame_gate({"original_source_pin":A.PIN,"scene":"turning",
                       "observation_grade":"CONTROLLER_SET"}),"NOT_ADMITTED_STATE_OR_CAPTURE_IS_NOT_PRESENT")
    def test_draw_submission_not_present(self):
        self.assertEqual(A.frame_gate({"original_source_pin":A.PIN,"scene":"raptor",
                       "observation_grade":"GPU_DRAW_SUBMITTED"}),"NOT_ADMITTED_STATE_OR_CAPTURE_IS_NOT_PRESENT")
    def test_forged_gpu_present_claim_stays_not_admitted(self):
        self.assertEqual(A.frame_gate({"original_source_pin":A.PIN,"scene":"raptor",
                       "observation_grade":"GPU_PRESENTED","renderer_token":"fake"}),
                       "NOT_ADMITTED_NO_SOURCE_ATTESTED_GPU_PRESENT_TOKEN")
    def test_unknown_provenance_refused(self):
        self.assertEqual(A.frame_gate({"original_source_pin":A.PIN,"scene":"turning",
                       "observation_grade":"other"}),"NOT_ADMITTED_NO_INDEPENDENT_PRESENT_PROOF")
    def test_redirection_original_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"r.js").symlink_to("/etc/hosts")
            with patch.dict(A.SOURCES,{"raptor":("r.js",A.SOURCES["raptor"][1])},clear=True):
                with self.assertRaises(ValueError):
                    A.run(root,root/"report.json")
    def test_no_report_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"r.js").write_bytes(RAPTOR)
            out=root/"audit.json";out.write_text("prior")
            with patch.dict(A.SOURCES,{"raptor":("r.js",fake_blob(RAPTOR))},clear=True):
                with self.assertRaises(ValueError):
                    A.run(root,out)
                self.assertEqual(out.read_text(),"prior")

if __name__=="__main__":unittest.main()
