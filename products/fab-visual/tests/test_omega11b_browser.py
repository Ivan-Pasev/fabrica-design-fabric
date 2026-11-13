"""Ω11B synthetic adversarial tests of finite browser-observation classifier."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

FILE = Path(__file__).resolve().parent.parent/"scripts"/"omega11b-browser-parity.py"
spec=importlib.util.spec_from_file_location("omega11b_browser_parity",FILE)
W=importlib.util.module_from_spec(spec);spec.loader.exec_module(W)


class BrowserEvidenceGuards(unittest.TestCase):
    def test_intra_run_jitter_is_not_equivalence(self):
        self.assertEqual(W.classify_pixels(True, True, False, True, {}, {}, []),
                         "INCONCLUSIVE_DYNAMIC_STATE")
        self.assertEqual(W.classify_pixels(True, True, True, False, {}, {}, []),
                         "INCONCLUSIVE_DYNAMIC_STATE")

    def test_page_error_forces_inconclusive(self):
        self.assertEqual(W.classify_pixels(True, True, True, True, {}, {}, ["request blocked"]),
                         "INCONCLUSIVE_RUNTIME")

    def test_dom_difference_visible_independently(self):
        self.assertEqual(W.classify_pixels(True, True, True, True,
                                          {"svg":3},{"svg":2},[]),
                         "OBSERVED_DOM_DELTA")

    def test_observed_pixel_difference(self):
        self.assertEqual(W.classify_pixels(False, False, True, True, {}, {}, []),
                         "OBSERVED_PIXEL_DELTA")

    def test_observed_identity_not_global_parity(self):
        self.assertEqual(W.classify_pixels(True, True, True, True, {}, {}, []),
                         "OBSERVED_IDENTICAL_PIXELS")

    def test_source_pin_is_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);rel="example.html";(base/rel).write_bytes(b"A")
            self.assertEqual(W.check_file(base,rel,W.sha(base/rel)),W.sha(base/rel))
            with self.assertRaises(ValueError):
                W.check_file(base,rel,"0"*64)

    def test_malformed_and_symlink_path_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            with self.assertRaises(ValueError):
                W.check_file(base,"missing.html")
            (base/"good.html").write_bytes(b"ok")
            (base/"shadow.html").symlink_to(base/"good.html")
            with self.assertRaises(ValueError):
                W.check_file(base,"shadow.html")

    def test_pixel_difference_not_hidden_by_alpha(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            a,b,d=(root/x for x in ("a.png","b.png","delta.png"))
            Image.new("RGBA",(2,2),(10,20,30,255)).save(a)
            Image.new("RGBA",(2,2),(10,20,30,255)).save(b)
            self.assertTrue(W.image_stats(a,b,d)["equal"])
            im=Image.open(b).convert("RGBA");im.putpixel((0,1),(11,20,30,255));im.save(b)
            report=W.image_stats(a,b,d)
            self.assertFalse(report["equal"])
            self.assertEqual(report["changed_pixels"],1)
            self.assertAlmostEqual(report["changed_fraction"],.25)

if __name__=="__main__":
    unittest.main()
