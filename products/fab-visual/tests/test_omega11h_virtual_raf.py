"""Ω11H virtual-clock interface and proof-boundary adversarial tests."""
import importlib.util
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parent.parent/"scripts"
spec=importlib.util.spec_from_file_location("omega11h_clock",HERE/"omega11h-virtual-raf.py")
K=importlib.util.module_from_spec(spec);spec.loader.exec_module(K)

def good():
    return {"schema":"fab.visual.omega11h.synthetic-raf.v1",
      "performance_now_virtualized":True,"intersections":1,
      "renderer_presented_frame":"NOT_ADMITTED",
      "steps":[{"now":ms,"delivered":1,"remaining":1} for ms in K.CLOCK_TIMES]}

class VirtualRafProofBoundary(unittest.TestCase):
    def test_exact_rational_schedule(self):
        self.assertEqual(K.strict_clock(good()),"PASS_TEST_ONLY_CLOCK_DRIVER")

    def test_no_observer_start_rejected(self):
        x=good();x["intersections"]=0
        self.assertEqual(K.strict_clock(x),"FAIL_SOURCE_VISIBILITY_GATE")

    def test_forged_presentation_rejected(self):
        x=good();x["renderer_presented_frame"]="GPU_PRESENTED"
        self.assertEqual(K.strict_clock(x),"FAIL_FORGED_RENDERER_FRAME")

    def test_opaque_clock_incomplete_rejected(self):
        x=good();x["steps"].pop()
        self.assertEqual(K.strict_clock(x),"FAIL_INCOMPLETE_VIRTUAL_INPUT")

    def test_wrong_clock_timestamps_rejected(self):
        x=good();x["steps"][1]["now"]+=.2
        self.assertEqual(K.strict_clock(x),"FAIL_NONMONOTONIC_OR_WRONG_RAF_SCHEDULE")

    def test_wrong_step_type_rejected(self):
        x=good();x["steps"][1]["delivered"]="one"
        self.assertEqual(K.strict_clock(x),"FAIL_NONMONOTONIC_OR_WRONG_RAF_SCHEDULE")

    def test_performance_now_not_virtual_rejected(self):
        x=good();x["performance_now_virtualized"]=False
        self.assertEqual(K.strict_clock(x),"FAIL_UNCONTROLLED_PERFORMANCE_NOW")

    def test_identity_mismatch_rejected(self):
        x=good();x["schema"]="REAL_RENDERER_CLOCK"
        self.assertEqual(K.strict_clock(x),"FAIL_CLOCK_IDENTITY")

    def test_script_declares_test_semantics_not_production(self):
        self.assertIn("TEST_ONLY_PRE_PAGE",K.SCRIPT)
        self.assertIn("NOT_ADMITTED",K.SCRIPT)
        self.assertIn("window.IntersectionObserver=class ControlledIntersectionObserver",K.SCRIPT)
        self.assertIn("window.requestAnimationFrame=(callback)",K.SCRIPT)
        self.assertIn("state.performance_now_virtualized=performance.now()===0",K.SCRIPT)

    def test_clock_has_exact_three_inputs(self):
        self.assertEqual(len(K.CLOCK_TIMES),3)
        self.assertTrue(all(x<y for x,y in zip(K.CLOCK_TIMES,K.CLOCK_TIMES[1:])))

if __name__=="__main__":unittest.main()
