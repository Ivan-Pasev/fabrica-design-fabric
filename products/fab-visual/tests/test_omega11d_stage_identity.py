"""Ω11D fail-closed source-backed stage identity controls."""
from pathlib import Path
import importlib.util
import unittest

FILE=Path(__file__).resolve().parent.parent/"scripts"/"omega11c-state-replay.py"
spec=importlib.util.spec_from_file_location("fab_omega11d_stage",FILE)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def witness(stage=".rp-stage", *, width=400,height=280, svg_width=400,
            svg_height=280, vb="0 0 760 560",inside=True,count=1,svg_count=1):
    return {
        "stage_selector":stage,
        "stage":{"count":count,"hit_inside_stage":inside,
                 "rect":[0,0,width,height],"aria_value_now":"0"},
        "primary_svg":{"count":svg_count,"width":svg_width,
                       "height":svg_height,"viewbox":vb}
    }


class StageIdentity(unittest.TestCase):
    def test_valid_raptor_stage(self):
        self.assertTrue(mod.validate_scene_target(witness(),".rp-stage"))

    def test_valid_turning_stage(self):
        self.assertTrue(mod.validate_scene_target(
            witness(stage=".ts-stage"),".ts-stage"))

    def test_decorative_svg_rejected(self):
        self.assertFalse(mod.validate_scene_target(
            witness(svg_width=12,svg_height=12,vb="0 0 12 12"),".rp-stage"))

    def test_wrong_stage_selector_rejected(self):
        self.assertFalse(mod.validate_scene_target(
            witness(stage=".rp-stage"),".ts-stage"))

    def test_pointer_outside_stage_rejected(self):
        self.assertFalse(mod.validate_scene_target(
            witness(inside=False),".rp-stage"))

    def test_duplicate_or_missing_stage_rejected(self):
        self.assertFalse(mod.validate_scene_target(
            witness(count=0),".rp-stage"))
        self.assertFalse(mod.validate_scene_target(
            witness(count=2),".rp-stage"))

    def test_stage_rectangle_too_small_rejected(self):
        self.assertFalse(mod.validate_scene_target(
            witness(width=11,height=12),".rp-stage"))

    def test_missing_svg_and_viewbox_rejected(self):
        self.assertFalse(mod.validate_scene_target(
            witness(svg_count=0),".rp-stage"))
        self.assertFalse(mod.validate_scene_target(
            witness(vb=""),".rp-stage"))
        self.assertFalse(mod.validate_scene_target(
            witness(vb="0 0 12"),".rp-stage"))

    def test_bad_snapshot_shape_rejected(self):
        self.assertFalse(mod.validate_scene_target(None,".rp-stage"))
        self.assertFalse(mod.validate_scene_target({},".rp-stage"))

    def test_full_replay_still_has_frame_boundary(self):
        self.assertEqual(mod.REPEATS,3)
        self.assertEqual(mod.PROCESSES,2)
        self.assertEqual(mod.STAGE_SELECTORS["raptor-light"],".rp-stage")
        self.assertEqual(mod.STAGE_SELECTORS["turning-light"],".ts-stage")
        self.assertEqual(mod.replay_classification({
            "pinned":[],"rebuilt":[]}),"INCOMPLETE")

if __name__=="__main__":
    unittest.main()
