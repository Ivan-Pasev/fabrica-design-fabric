"""Ω11G exact ordinal checkpoints / dual derivatives / non-admission tests."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent.parent/"scripts"
def load(file):
    s=importlib.util.spec_from_file_location(file.replace("-","_"),HERE/file)
    m=importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

K=load("omega11g-checkpoint-derivative.py")
B=load("omega11g-checkpoint-browser.py")
RAPTOR=(b"<html><script>\nfunction tick(now) {\n"
        b"  if (!burn.on) say(idleText());\n"
        b"  frame = visible && (moving || burning || touring) ? requestAnimationFrame(tick) : 0;\n}\n"
        b"function run() {\nif (!frame && visible) {\n frame=1;\n }\n}\n</script></html>\n")
TURNING=(b"<html><script>\nfunction tick(now) {\n"
         b"    controller.set({ table: angle, lift: 1, time });\n    slow = 3;\n"
         b"  frame = visible && touring ? requestAnimationFrame(tick) : 0;\n}\n"
         b"new IntersectionObserver((entries)=>{\n"
         b"if (visible && touring && !frame) frame = requestAnimationFrame(tick);\n});\n"
         b"</script></html>\n")


def meta(scene,raw,name):
    m=dict(K.D.SCENES[scene])
    m["sha"]=K.sha(raw)
    m["relative"]=name
    return m


def observation(scene,mode):
    state=({"burn":{},"springs":{}} if scene=="raptor-light"
           else {"applied_controller_state":{"table":3,"lift":1,"time":.03}})
    return {
     "schema":"fab.visual.omega11g.control.v1","scene":scene,
     "mode":mode,"target":3,"serial":3,"done":True,
     "actual_renderer_frame":"NOT_ADMITTED","actual_mesh_depth":"NOT_RUN",
     "events":([] if mode=="MINIMAL_CHECKPOINT" else [
       {"serial":i,"applied_state":copy.deepcopy(state),"renderer_present_barrier":"NOT_AVAILABLE"}
       for i in (1,2,3)])
    }


class CheckpointDerivative(unittest.TestCase):
    def test_exact_raptor_patch_modes(self):
        with patch.dict(K.D.SCENES,{"raptor-light":meta("raptor-light",RAPTOR,"r.html")},clear=True):
            for mode in K.MODES:
                result,record=K.patch("raptor-light",RAPTOR,mode)
                self.assertIn(b"__fab11gApplied(now);",result)
                self.assertIn(b"!window.__fab11gControl.done",result)
                self.assertEqual(record["checkpoint_target"],3)
                self.assertEqual(record["renderer_presented_frame"],"NOT_ADMITTED")
                self.assertNotEqual(result,RAPTOR)

    def test_exact_turning_patch_modes(self):
        with patch.dict(K.D.SCENES,{"turning-light":meta("turning-light",TURNING,"t.html")},clear=True):
            for mode in K.MODES:
                result,record=K.patch("turning-light",TURNING,mode)
                self.assertIn(b"__fab11gApplied(now);",result)
                self.assertIn(b"!window.__fab11gControl.done",result)
                self.assertEqual(record["real_mesh_depth"],"NOT_RUN")

    def test_original_hash_mismatch_refused(self):
        with patch.dict(K.D.SCENES,{"raptor-light":meta("raptor-light",RAPTOR,"r.html")},clear=True):
            with self.assertRaises(ValueError):
                K.patch("raptor-light",RAPTOR+b"changed","OBSERVING_CHECKPOINT")

    def test_missing_scheduler_anchor_refused(self):
        wrong=RAPTOR.replace(b"requestAnimationFrame(tick)",b"requestAnimationFrame(other)",1)
        with patch.dict(K.D.SCENES,{"raptor-light":meta("raptor-light",wrong,"r.html")},clear=True):
            with self.assertRaises(ValueError):
                K.patch("raptor-light",wrong,"MINIMAL_CHECKPOINT")

    def test_duplicate_tick_anchor_refused(self):
        dup=RAPTOR+b"function tick(now) {"
        with patch.dict(K.D.SCENES,{"raptor-light":meta("raptor-light",dup,"r.html")},clear=True):
            with self.assertRaises(ValueError):
                K.patch("raptor-light",dup,"MINIMAL_CHECKPOINT")

    def test_previously_instrumented_source_refused(self):
        wrong=RAPTOR+b"__fab11gControl"
        with patch.dict(K.D.SCENES,{"raptor-light":meta("raptor-light",wrong,"r.html")},clear=True):
            with self.assertRaises(ValueError):
                K.patch("raptor-light",wrong,"MINIMAL_CHECKPOINT")

    def test_unknown_mode_refused(self):
        with self.assertRaises(ValueError):
            K.patch("raptor-light",RAPTOR,"SOURCE_ORIGINAL")

    def test_original_and_derivatives_are_separate(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);original=p/"original";minimal=p/"minimal";observing=p/"observing"
            for root in (original,minimal,observing):
                root.mkdir()
                (root/"r.html").write_bytes(RAPTOR)
                (root/"t.html").write_bytes(TURNING)
            entries={"raptor-light":meta("raptor-light",RAPTOR,"r.html"),
                     "turning-light":meta("turning-light",TURNING,"t.html")}
            with patch.dict(K.D.SCENES,entries,clear=True):
                r=K.create(original,minimal,observing,p/"manifest.json")
                self.assertEqual(len(r["variants"]),4)
                self.assertEqual((original/"r.html").read_bytes(),RAPTOR)
                self.assertEqual((original/"t.html").read_bytes(),TURNING)
                self.assertNotEqual((minimal/"r.html").read_bytes(),RAPTOR)
                self.assertNotEqual((observing/"t.html").read_bytes(),TURNING)
                self.assertEqual(r["frame_attestation"],"NOT_ADMITTED")

    def test_nested_original_and_derivatives_refused(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);a=p/"a";b=a/"b";c=p/"c"
            for x in (a,b,c):x.mkdir()
            with self.assertRaises(ValueError):
                K.create(a,b,c,p/"m.json")


class BrowserAdversarial(unittest.TestCase):
    def test_true_minimal_checkpoint_ordinal(self):
        self.assertEqual(B.verify_checkpoint("raptor-light","minimal",
                           observation("raptor-light","MINIMAL_CHECKPOINT")),
                           "PASS_FIXED_APPLICATION_ORDINAL_ONLY")

    def test_true_observing_checkpoint_ordinal(self):
        self.assertEqual(B.verify_checkpoint("turning-light","observing",
                           observation("turning-light","OBSERVING_CHECKPOINT")),
                           "PASS_FIXED_APPLICATION_ORDINAL_ONLY")

    def test_wrong_serial_or_unfrozen_rejected(self):
        c=observation("raptor-light","MINIMAL_CHECKPOINT")
        c["serial"]=4
        self.assertEqual(B.verify_checkpoint("raptor-light","minimal",c),"FAIL_WRONG_APPLIED_ORDINAL")
        c["serial"]=3;c["done"]=False
        self.assertEqual(B.verify_checkpoint("raptor-light","minimal",c),"FAIL_NOT_FROZEN_AT_ORDINAL")

    def test_fake_frame_or_depth_rejected(self):
        c=observation("turning-light","OBSERVING_CHECKPOINT")
        c["actual_renderer_frame"]="FRAME_VERIFIED"
        self.assertEqual(B.verify_checkpoint("turning-light","observing",c),
                         "FAIL_FORGED_FRAME_DEPTH_ADMISSION")
        c["actual_renderer_frame"]="NOT_ADMITTED";c["actual_mesh_depth"]="PASS"
        self.assertEqual(B.verify_checkpoint("turning-light","observing",c),
                         "FAIL_FORGED_FRAME_DEPTH_ADMISSION")

    def test_event_order_and_count_rejected(self):
        c=observation("raptor-light","OBSERVING_CHECKPOINT")
        c["events"][1]["serial"]=1
        self.assertEqual(B.verify_checkpoint("raptor-light","observing",c),"FAIL_EVENT_SEQUENCE")

    def test_missing_controller_state_rejected(self):
        c=observation("turning-light","OBSERVING_CHECKPOINT")
        c["events"][1]["applied_state"].pop("applied_controller_state")
        self.assertEqual(B.verify_checkpoint("turning-light","observing",c),"FAIL_CONTROLLER_STATE")

    def test_wrong_scene_rejected(self):
        c=observation("turning-light","OBSERVING_CHECKPOINT")
        self.assertEqual(B.verify_checkpoint("raptor-light","observing",c),"FAIL_SCENE")

    def test_minimal_with_hidden_observer_rejected(self):
        c=observation("raptor-light","MINIMAL_CHECKPOINT")
        c["events"].append({"serial":1})
        self.assertEqual(B.verify_checkpoint("raptor-light","minimal",c),
                         "FAIL_MINIMAL_NOT_MINIMAL")

    def test_false_present_barrier_rejected(self):
        c=observation("turning-light","OBSERVING_CHECKPOINT")
        c["events"][0]["renderer_present_barrier"]="GPU_PRESENTED"
        self.assertEqual(B.verify_checkpoint("turning-light","observing",c),
                         "FAIL_FORGED_PRESENT_BARRIER")


if __name__=="__main__":unittest.main()
