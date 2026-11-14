"""Ω11F adversarial source derivative and runtime-readout boundary checks."""
from __future__ import annotations
from contextlib import ExitStack
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS=Path(__file__).resolve().parent.parent/"scripts"


def load(name):
    spec=importlib.util.spec_from_file_location(name.replace("-","_"),
                                                SCRIPTS/name)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


D=load("omega11f-derivative.py")
B=load("omega11f-browser-witness.py")
RAPTOR_TEST=(b"HEAD\nconst D = {};\nfunction tick(now) {\n"
             b"  if (!burn.on) say(idleText());\n  frame = visible;\n}\n")
TURNING_TEST=(b"HEAD\nconst DATA = {};\nfunction tick(now) {\n"
              b"    controller.set({ table: angle, lift: 1, time });\n    slow = 3;\n}\n")


def fixture(scene,raw):
    d=dict(D.SCENES[scene]);d["sha"]=D.sha(raw)
    return d


def tick_event(scene,seq=1):
    if scene=="raptor-light":
        return {"seq":seq,"renderer_present_barrier":"NOT_AVAILABLE",
                "frame_provenance":"AFTER_TICK_DOM_UPDATE_BEFORE_NEXT_RAF",
                "springs":{"a":{"x":0,"target":0}},
                "gl_camera_static":{},"app_clock":.1}
    return {"seq":seq,"renderer_present_barrier":"NOT_AVAILABLE",
            "frame_provenance":"AFTER_CONTROLLER_SET_BEFORE_NEXT_RAF",
            "applied_controller_state":{"table":5,"lift":1,"time":.2}}


def frame(scene):
    return {"schema":"fab.visual.omega11f.derivative.v1",
            "scene":scene,"source_commit":D.PIN,
            "intervention":"ADDITIVE_TEST_HOOK",
            "camera_grade":("SOURCE_STATIC" if scene=="raptor-light" else "NOT_AVAILABLE"),
            "runtime_frame_attested":False,"depth_order_attested":False,
            "events":[tick_event(scene,1),tick_event(scene,2)]}


class DerivativeContract(unittest.TestCase):
    def test_raptor_exact_hash_boot_and_hook(self):
        with patch.dict(D.SCENES,{"raptor-light":fixture("raptor-light",RAPTOR_TEST)},clear=True):
            derived,receipt=D.inject("raptor-light",RAPTOR_TEST)
            self.assertIn(b"__fab11fCaptureRaptor(now);",derived)
            self.assertIn(b"runtime_frame_attested:false",derived)
            self.assertNotEqual(D.sha(derived),D.sha(RAPTOR_TEST))
            self.assertFalse(receipt["derivative_is_original"])

    def test_turning_controller_exact_hook(self):
        with patch.dict(D.SCENES,{"turning-light":fixture("turning-light",TURNING_TEST)},clear=True):
            derived,receipt=D.inject("turning-light",TURNING_TEST)
            self.assertIn(b"__fab11fCaptureTurning(now);",derived)
            self.assertIn(b"AFTER_CONTROLLER_SET_BEFORE_NEXT_RAF",derived)
            self.assertEqual(receipt["real_renderer_depth"],"NOT_RUN")

    def test_wrong_source_hash_rejected(self):
        with patch.dict(D.SCENES,{"raptor-light":fixture("raptor-light",RAPTOR_TEST)},clear=True):
            with self.assertRaises(ValueError):
                D.inject("raptor-light",RAPTOR_TEST+b"tamper")

    def test_missing_or_repeated_anchor_rejected(self):
        bad=RAPTOR_TEST.replace(b"function tick(now) {",b"function wrong(now) {")
        with patch.dict(D.SCENES,{"raptor-light":fixture("raptor-light",bad)},clear=True):
            with self.assertRaises(ValueError):
                D.inject("raptor-light",bad)
        duplicate=RAPTOR_TEST+b"function tick(now) {"
        with patch.dict(D.SCENES,{"raptor-light":fixture("raptor-light",duplicate)},clear=True):
            with self.assertRaises(ValueError):
                D.inject("raptor-light",duplicate)

    def test_source_already_instrumented_rejected(self):
        bad=RAPTOR_TEST+b"\nconst __fab11fDerivative = 5;"
        with patch.dict(D.SCENES,{"raptor-light":fixture("raptor-light",bad)},clear=True):
            with self.assertRaises(ValueError):
                D.inject("raptor-light",bad)

    def test_source_and_derivative_separate(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            origin=base/"original";derived=base/"derivative"
            origin.mkdir();derived.mkdir()
            with patch.dict(D.SCENES,{"raptor-light":fixture("raptor-light",RAPTOR_TEST)},clear=True):
                (origin/"examples").mkdir();(derived/"examples").mkdir()
                (origin/"examples/page.html").write_bytes(RAPTOR_TEST)
                (derived/"examples/page.html").write_bytes(RAPTOR_TEST)
                D.SCENES["raptor-light"]["relative"]="examples/page.html"
                manifest=D.apply(origin,derived,base/"manifest.json")
                self.assertEqual((origin/"examples/page.html").read_bytes(),RAPTOR_TEST)
                self.assertIn(b"__fab11fCaptureRaptor", (derived/"examples/page.html").read_bytes())
                self.assertEqual(manifest["runtime_renderer_attestation"],"NOT_ADMITTED")
                self.assertEqual(manifest["release"],"HOLD")

    def test_original_equals_derivative_path_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            with self.assertRaises(ValueError): D.apply(p,p,p/"m.json")

    def test_missing_second_original_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/"a";b=Path(td)/"b";a.mkdir();b.mkdir()
            (a/"r.html").write_bytes(RAPTOR_TEST);(b/"r.html").write_bytes(RAPTOR_TEST)
            entries={"raptor-light":{**fixture("raptor-light",RAPTOR_TEST),"relative":"r.html"},
                     "turning-light":{**fixture("turning-light",TURNING_TEST),"relative":"t.html"}}
            with patch.dict(D.SCENES,entries,clear=True):
                with self.assertRaises(ValueError):
                    D.apply(a,b,Path(td)/"manifest.json")
            self.assertEqual((b/"r.html").read_bytes(),RAPTOR_TEST)

    def test_symlinked_source_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);src=root/"source";src.write_bytes(RAPTOR_TEST)
            (root/"link.html").symlink_to(src)
            with self.assertRaises(ValueError):
                D.checked_file(root,"link.html")

    def test_not_known_scene_rejected(self):
        with self.assertRaises(ValueError):D.inject("not-a-real-scene",RAPTOR_TEST)


class RuntimeNonpromotion(unittest.TestCase):
    def test_valid_instrumented_raptor_is_not_full_frame_attestation(self):
        self.assertEqual(B.assess("raptor-light",frame("raptor-light")),
                         "PASS_INSTRUMENTED_STATE_READOUT_ONLY")

    def test_valid_instrumented_turning(self):
        self.assertEqual(B.assess("turning-light",frame("turning-light")),
                         "PASS_INSTRUMENTED_STATE_READOUT_ONLY")

    def test_forged_frame_attestation_rejected(self):
        r=frame("raptor-light");r["runtime_frame_attested"]=True
        self.assertEqual(B.assess("raptor-light",r),"FAIL_UNSUPPORTED_FRAME_ADMISSION")

    def test_forged_depth_attestation_rejected(self):
        r=frame("turning-light");r["depth_order_attested"]=True
        self.assertEqual(B.assess("turning-light",r),"FAIL_UNSUPPORTED_DEPTH_ADMISSION")

    def test_camera_grade_mismatch_rejected(self):
        r=frame("turning-light");r["camera_grade"]="RUNTIME_READBACK"
        self.assertEqual(B.assess("turning-light",r),"FAIL_CAMERA_GRADE")

    def test_frame_sequence_disorder_rejected(self):
        r=frame("raptor-light");r["events"][1]["seq"]=1
        self.assertEqual(B.assess("raptor-light",r),"FAIL_NONMONOTONIC_TICK")

    def test_false_present_barrier_rejected(self):
        r=frame("turning-light");r["events"][1]["renderer_present_barrier"]="ATTESTED"
        self.assertEqual(B.assess("turning-light",r),"FAIL_UNSUPPORTED_PRESENT_BARRIER")

    def test_missing_controller_state_rejected(self):
        r=frame("turning-light");r["events"][0]["applied_controller_state"].pop("time")
        self.assertEqual(B.assess("turning-light",r),"FAIL_MISSING_CONTROLLER_STATE")

    def test_missing_update_inconclusive(self):
        r=frame("raptor-light");r["events"]=r["events"][:1]
        self.assertEqual(B.assess("raptor-light",r),"INCONCLUSIVE_TOO_FEW_UPDATES")
        self.assertEqual(B.assess("raptor-light",None),"INCONCLUSIVE_MISSING_READOUT")

    def test_wrong_source_or_wrong_hook_rejected(self):
        r=frame("raptor-light");r["source_commit"]="fake"
        self.assertEqual(B.assess("raptor-light",r),"FAIL_SOURCE_IDENTITY")
        r=frame("raptor-light");r["events"][0]["frame_provenance"]="untrusted"
        self.assertEqual(B.assess("raptor-light",r),"FAIL_WRONG_RAPTOR_HOOK")


if __name__=="__main__":
    unittest.main()
