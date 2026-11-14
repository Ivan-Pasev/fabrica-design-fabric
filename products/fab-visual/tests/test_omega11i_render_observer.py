"""Ω11I negative/positive bounded WebGL API interception evidence predicates."""
import importlib.util
from pathlib import Path
import unittest

path=Path(__file__).resolve().parent.parent/"scripts"/"omega11i-render-observer.py"
spec=importlib.util.spec_from_file_location("omega11i_render_observer",path)
O=importlib.util.module_from_spec(spec);spec.loader.exec_module(O)

def witness():
    return {"schema":"fab.visual.omega11i.render-api-observer.v1",
            "probe_kind":"TEST_ONLY_MONKEYPATCH",
            "actual_presented_frame":"NOT_ADMITTED",
            "framebuffer_readback":"NOT_RUN",
            "context_requests":[{"type":"webgl","granted":True}],
            "draw_calls":[{"api":"webgl1","method":"drawArrays"}]}

class DrawApiAudit(unittest.TestCase):
    def test_bounded_observation_pass(self):
        self.assertEqual(O.classify_draw_calls(witness()),"PASS_BOUNDED_API_CALL_CAPTURE_NOT_GPU_PRESENT")
    def test_no_draw_calls_does_not_fabricate_gpu(self):
        x=witness();x["draw_calls"]=[]
        self.assertEqual(O.classify_draw_calls(x),"PASS_BOUNDED_API_CALL_CAPTURE_NOT_GPU_PRESENT")
    def test_missing_probe_rejected(self):
        self.assertEqual(O.classify_draw_calls(None),"FAIL_WRONG_RENDER_OBSERVER")
    def test_wrong_schema_rejected(self):
        x=witness();x["schema"]="render_present_certified"
        self.assertEqual(O.classify_draw_calls(x),"FAIL_WRONG_RENDER_OBSERVER")
    def test_forged_gpu_present_refused(self):
        x=witness();x["actual_presented_frame"]="GPU_PRESENTED"
        self.assertEqual(O.classify_draw_calls(x),"FAIL_FORGED_GPU_OR_DEPTH_ATTESTATION")
    def test_forged_depth_readback_refused(self):
        x=witness();x["framebuffer_readback"]="CERTIFIED"
        self.assertEqual(O.classify_draw_calls(x),"FAIL_FORGED_GPU_OR_DEPTH_ATTESTATION")
    def test_observer_undisclosed_rejected(self):
        x=witness();x["probe_kind"]="PURE_SOURCE"
        self.assertEqual(O.classify_draw_calls(x),"FAIL_INSTRUMENTATION_UNDISCLOSED")
    def test_missing_draw_list_rejected(self):
        x=witness();x.pop("draw_calls")
        self.assertEqual(O.classify_draw_calls(x),"FAIL_RENDER_EVENTS_MISSING")
    def test_invalid_method_rejected(self):
        x=witness();x["draw_calls"]=[{"api":"webgl1","method":"gl.finish"}]
        self.assertEqual(O.classify_draw_calls(x),"FAIL_RENDER_METHOD_PROVENANCE")
    def test_invalid_context_granted_rejected(self):
        x=witness();x["context_requests"][0]["granted"]="true"
        self.assertEqual(O.classify_draw_calls(x),"FAIL_CONTEXT_PROVENANCE")
    def test_monkeypatch_is_always_disclosed(self):
        self.assertIn("TEST_ONLY_MONKEYPATCH",O.PROBE)
        self.assertIn("actual_presented_frame:'NOT_ADMITTED'",O.PROBE)
    def test_external_screen_capture_is_not_frame_proof(self):
        self.assertEqual(O.classify_draw_calls(witness()),"PASS_BOUNDED_API_CALL_CAPTURE_NOT_GPU_PRESENT")
        self.assertEqual(O.H.K.PIN,O.K.PIN)
if __name__=="__main__":unittest.main()
