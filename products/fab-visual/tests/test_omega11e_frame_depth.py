"""Ω11E: synthetic camera-ray/triangle oracle and non-admission adversarial controls."""
import importlib.util
import json
import math
from pathlib import Path
import unittest

FILE=Path(__file__).resolve().parent.parent/"scripts"/"omega11e-frame-depth.py"
spec=importlib.util.spec_from_file_location("omega11e_depth",FILE)
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


VIEW=((1.,0,0,0),(0,1.,0,0),(0,0,1.,0),(0,0,0,1.))
PROJECT=M.perspective(math.pi/2,1,1,10)


def ray():
    return M.camera_ray(VIEW,PROJECT,(0,0),(1,1),unit="m")


def tri(z,tid="one",part="component",flip=False,):
    points=[(-2,-2,z),(2,-2,z),(0,2,z)]
    if flip:points=[points[0],points[2],points[1]]
    return {"triangle_id":tid,"part_id":part,"vertices":points}


def evidence(value,grade="SOURCE_STATIC"):
    return {"value":value,"grade":grade}


def witness(grade="SOURCE_STATIC",frame_token="frame-7"):
    return {
        "source_commit":evidence(M.PIN),
        "source_html_sha256":evidence("0"*64),
        "model_sha256":evidence("1"*64),
        "scene_id":evidence("raptor-light"),
        "frame_event_id":evidence(frame_token,grade),
        "camera_pose":evidence({"frame_event_id":frame_token,"view_matrix":VIEW},grade),
        "camera_projection":evidence({"frame_event_id":frame_token,"matrix":PROJECT},grade),
        "visible_part_ids":evidence(["component"],grade),
        "viewport":evidence([1,1],grade),
        "renderer_version":evidence("test-only",grade)
    }


class IndependentFrameDepth(unittest.TestCase):
    def test_opengl_unproject_center_near_far(self):
        r=ray()
        self.assertAlmostEqual(r["origin"][2],-1.0,places=9)
        self.assertAlmostEqual(r["far_world"][2],-10.0,places=8)
        self.assertAlmostEqual(r["direction"][2],-1.0,places=9)
        self.assertAlmostEqual(r["max_t"],9.,places=8)

    def test_front_back_depth_order_when_input_reversed(self):
        outcome=M.ordered_depth(ray(),[tri(-4,"back","back"),
                                      tri(-2,"front","front")])
        self.assertEqual(outcome["state"],"FINITE_RAY_HIT")
        self.assertEqual([h["part_id"] for h in outcome["ordered_hits"]],["front","back"])
        self.assertTrue(all(h["front_face"] for h in outcome["ordered_hits"]))
        self.assertEqual(outcome["real_anatomy_depth_order"],"NOT_RUN")

    def test_backface_winding(self):
        r=M.ordered_depth(ray(),[tri(-2,flip=True)])
        self.assertEqual(r["state"],"FINITE_RAY_HIT")
        self.assertFalse(r["ordered_hits"][0]["front_face"])

    def test_near_and_far_clipping(self):
        r=M.ordered_depth(ray(),[tri(-.5,"n"),tri(-11,"f")])
        self.assertEqual(r["state"],"FINITE_RAY_EMPTY")

    def test_tie_is_inconclusive_not_arbitrary_priority(self):
        o=M.ordered_depth(ray(),[tri(-2,"one"),tri(-2,"two")])
        self.assertEqual(o["state"],"INCONCLUSIVE_BOUNDARY_OR_TIE")
        self.assertEqual(len(o["ordered_hits"]),2)

    def test_uncertainty_induced_tie(self):
        o=M.ordered_depth(ray(),[tri(-2,"one"),tri(-2.0002,"two")],
                          uncertainty=.001)
        self.assertEqual(o["state"],"INCONCLUSIVE_BOUNDARY_OR_TIE")

    def test_edge_hit_is_boundary(self):
        # Point (0,0,-2) on an edge between (-1,0,-2) and (1,0,-2)
        t={"triangle_id":"edge","part_id":"part","vertices":[
             (-1,0,-2),(1,0,-2),(0,2,-2)]}
        o=M.ordered_depth(ray(),[t])
        self.assertEqual(o["state"],"INCONCLUSIVE_BOUNDARY_OR_TIE")

    def test_parallel_ray_miss(self):
        t={"triangle_id":"parallel","part_id":"part","vertices":[
             (2,-1,-2),(2,1,-2),(2,0,-4)]}
        self.assertEqual(M.ordered_depth(ray(),[t])["state"],"FINITE_RAY_EMPTY")

    def test_degenerate_triangle_rejected(self):
        with self.assertRaises(ValueError):
            M.ordered_depth(ray(),[{"triangle_id":"bad","part_id":"part",
                "vertices":[(0,0,-2),(1,1,-2),(2,2,-2)]}])

    def test_duplicate_triangle_id_rejected(self):
        with self.assertRaises(ValueError):
            M.ordered_depth(ray(),[tri(-2),tri(-3)])

    def test_malformed_and_noninvertible_camera_rejected(self):
        singular=((1,0,0,0),(0,0,0,0),(0,0,1,0),(0,0,0,1))
        with self.assertRaises(ValueError):
            M.camera_ray(singular,PROJECT,(0,0),(1,1),unit="m")
        with self.assertRaises(ValueError):
            M.camera_ray(VIEW,((1,0),(0,1)),(0,0),(1,1),unit="m")

    def test_invalid_near_far_perspective(self):
        with self.assertRaises(ValueError):
            M.perspective(math.pi/2,1,10,1)
        with self.assertRaises(ValueError):
            M.perspective(math.pi/2,1,0,1)

    def test_units_and_out_of_viewport_rejected(self):
        with self.assertRaises(ValueError):
            M.camera_ray(VIEW,PROJECT,(0,0),(1,1),unit="mm")
        with self.assertRaises(ValueError):
            M.camera_ray(VIEW,PROJECT,(1,0),(1,1),unit="m")
        with self.assertRaises(ValueError):
            M.ordered_depth({**ray(),"unit":"mm"},[tri(-2)])

    def test_nonfinite_nan_and_bool_rejected(self):
        with self.assertRaises(ValueError):
            M.ordered_depth(ray(),[tri(math.nan)])
        with self.assertRaises(ValueError):
            M.camera_ray(VIEW,PROJECT,(False,0),(1,1),unit="m")

    def test_mislinked_frame_rejected_by_contract(self):
        w=witness("RUNTIME_READBACK")
        w["camera_pose"]["value"]["frame_event_id"]="other"
        c=M.frame_contract(w)
        self.assertEqual(c["contract_status"],"INCOMPLETE_PROVENANCE")
        self.assertEqual(c["authoritative_frame_verified"],"NOT_ADMITTED")

    def test_static_model_camera_does_not_admit_runtime_frame(self):
        c=M.frame_contract(witness())
        self.assertEqual(c["contract_status"],"INCOMPLETE_PROVENANCE")
        self.assertEqual(c["rendered_camera_geometry_verified"],"NOT_ADMITTED")

    def test_fake_runtime_fields_not_independent_attestation(self):
        c=M.frame_contract(witness("RUNTIME_READBACK"))
        self.assertEqual(c["contract_status"],"DECLARED_FRAME_FIELDS_CONSISTENT")
        self.assertEqual(c["authoritative_frame_verified"],"NOT_ADMITTED")
        self.assertEqual(c["independent_runtime_attestation"],"NOT_AVAILABLE")
        self.assertEqual(c["release"],"HOLD")

    def test_forged_source_and_hash_fail(self):
        w=witness()
        w["source_commit"]["value"]="fake"
        with self.assertRaises(ValueError):
            M.frame_contract(w)
        w=witness()
        w["model_sha256"]["value"]="0"*63
        with self.assertRaises(ValueError):
            M.frame_contract(w)

    def test_missing_grade_fail_closed(self):
        w=witness()
        del w["camera_pose"]["grade"]
        with self.assertRaises(ValueError):
            M.frame_contract(w)

    def test_expected_synthetic_receipt_boundary(self):
        doc=M.example_receipt()
        self.assertEqual(doc["synthetic_depth_case"]["state"],"FINITE_RAY_HIT")
        self.assertEqual(doc["real_renderer_frame"],"NOT_ADMITTED")
        self.assertEqual(doc["real_anatomy_occlusion"],"NOT_RUN")
        self.assertEqual(doc["byte_parity"],"FAIL")
        self.assertEqual(doc["release"],"HOLD")


if __name__=="__main__":
    unittest.main()
