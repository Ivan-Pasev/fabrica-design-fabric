"""Ω11C adversarial tests: source provenance, transparent-pixel trap, crossrun."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from PIL import Image


def load(fname):
    path=Path(__file__).resolve().parent.parent/"scripts"/fname
    spec=importlib.util.spec_from_file_location(fname.replace("-","_").replace(".py",""),path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

A=load("omega11c-crossrun-audit.py")
R=load("omega11c-state-replay.py")


def png(rgb):
    stream=io.BytesIO()
    Image.new("RGBA",(4,4),(*rgb,255)).save(stream,format="PNG")
    return stream.getvalue()


def fake_zip(path, *, changed=False, bad_hash=False, pin=A.PIN, config=None):
    shots={}
    observations=[]
    for i in range(A.CASES):
        case=f"synthetic-{i:02d}"
        receipt_images={}
        for side in ("original","rebuilt"):
            color=(30,30,30) if not(changed and i==5 and side=="rebuilt") else (31,30,30)
            data=png(color)
            repeat=data
            shots[f"captures/{case}-{side}-capture.png"]=data
            shots[f"captures/{case}-{side}-repeat.png"]=repeat
            receipt_images[side]={"capture":A.digest(data),"repeat":A.digest(repeat)}
        observations.append({"case":case,"classification":"OBSERVED_IDENTICAL_PIXELS" if not(changed and i==5) else "OBSERVED_PIXEL_DELTA",
                             "original_stable":True,"rebuilt_stable":True,
                             "captures":receipt_images})
    if bad_hash:
        shots["captures/synthetic-00-original-capture.png"]=png((255,0,0))
    receipt={"source_pin":pin,"release":"HOLD",
             "strict_generated_byte_parity":"FAIL",
             "observation_coverage":"EXECUTED","completed_cases":A.CASES,
             "runtime_failures":[],"observations":observations,
             "source_hashes":{"synthetic":{"pinned":"abc","rebuilt":"def"}},
             "config":config or {"width":390},"browser_version":"test-Chromium",
             "playwright_version":"test"}
    with zipfile.ZipFile(path,"w") as archive:
        archive.writestr(A.RECEIPT,json.dumps(receipt))
        for name,data in shots.items():
            archive.writestr(name,data)


def replay_side(value="X",obs=None):
    item={"frames":[value]*R.REPEATS,"observation":obs or {"hover":"x"},
          "pointer":{"x":5,"y":6},"live_camera":{"source":"UNAVAILABLE"},
          "errors":[],"blocked":[]}
    return [json.loads(json.dumps(item)) for _ in range(R.PROCESSES)]


class Omega11CContracts(unittest.TestCase):
    def test_source_embed_and_lock(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);p=root/"test.html"
            p.write_text('HEAD\nconst D = {"camera":{"k":1.0},"V":[1,2,3]};\nEND')
            f=R.source_fingerprint(root,"test.html","D",R.digest(p.read_bytes()))
            self.assertEqual(f["model_constant"],"D")
            with self.assertRaises(ValueError):
                R.source_fingerprint(root,"test.html","D","0"*64)
            with self.assertRaises(ValueError):
                R.source_fingerprint(root,"test.html","DATA")

    def test_replay_finite_identity(self):
        self.assertEqual(R.replay_classification({"pinned":replay_side(),
                                                  "rebuilt":replay_side()}),
                         "PASS_FINITE_REPLAY_ONLY")

    def test_replay_baseline_delta_not_promotion(self):
        self.assertEqual(R.replay_classification({"pinned":replay_side("A"),
                                                  "rebuilt":replay_side("B")}),
                         "OBSERVED_BASELINE_CANDIDATE_PIXEL_DELTA")

    def test_replay_process_jitter_rejected(self):
        s=replay_side();s[1]["frames"]=["B"]*R.REPEATS
        self.assertEqual(R.replay_classification({"pinned":s,"rebuilt":replay_side()}),
                         "FAIL_CROSS_PROCESS_PIXELS")

    def test_replay_state_mismatch_rejected(self):
        s=replay_side();s[1]["observation"]["hover"]="different"
        self.assertEqual(R.replay_classification({"pinned":s,"rebuilt":replay_side()}),
                         "FAIL_CROSS_PROCESS_STATE_OBSERVATION")

    def test_replay_within_process_rejected(self):
        s=replay_side();s[0]["frames"][1]="DELTA"
        self.assertEqual(R.replay_classification({"pinned":s,"rebuilt":replay_side()}),
                         "FAIL_WITHIN_PROCESS_PIXELS")

    def test_replay_blocked_resource_fail_closed(self):
        s=replay_side();s[0]["blocked"]=["https://bad.example"]
        self.assertEqual(R.replay_classification({"pinned":s,"rebuilt":replay_side()}),
                         "INCONCLUSIVE_RUNTIME")

    def test_replay_missing_process_fails(self):
        self.assertEqual(R.replay_classification({"pinned":replay_side()[:1],
                                                  "rebuilt":replay_side()}),
                         "INCOMPLETE")

    def test_pixel_overlay_visible_when_alpha_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            before=Image.open(io.BytesIO(png((100,100,100)))).convert("RGBA")
            after=before.copy();after.putpixel((2,1),(101,100,100,255))
            out=Path(td)/"evidence.png"
            stats=A.compare_images(before,after,out)
            self.assertEqual(stats["changed_pixels"],1)
            self.assertEqual(stats["max_channel_delta"],1)
            self.assertEqual(stats["bbox"],[2,1,3,2])
            self.assertEqual(Image.open(out).convert("RGBA").getpixel((2,1)),(255,0,0,255))

    def test_archive_provenance_and_crossrun_diff(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td);pa=path/"a.zip";pb=path/"b.zip"
            fake_zip(pa);fake_zip(pb,changed=True)
            report,code=A.compare_archives(A.Evidence(pa),A.Evidence(pb),path/"out")
            self.assertEqual(code,0)
            self.assertEqual(report["cross_run_pixel_reproducibility"],"FAIL")
            self.assertEqual(report["crossrun_image_drift_cases"],1)
            self.assertEqual(report["case_classification_mismatches"],1)
            self.assertEqual(report["release"],"HOLD")

    def test_archive_source_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);a=root/"a.zip";b=root/"b.zip"
            fake_zip(a);fake_zip(b,config={"different":True})
            with self.assertRaises(ValueError):
                A.compare_archives(A.Evidence(a),A.Evidence(b),root/"out")

    def test_tampered_screenshot_sha_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);a=root/"a.zip";b=root/"b.zip"
            fake_zip(a,bad_hash=True);fake_zip(b)
            with self.assertRaises(ValueError):
                A.compare_archives(A.Evidence(a),A.Evidence(b),root/"out")

    def test_wrong_source_pin_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"bad.zip";fake_zip(p,pin="WRONG")
            with self.assertRaises(ValueError):A.Evidence(p)

    def test_zip_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"traversal.zip"
            with zipfile.ZipFile(p,"w") as z:
                z.writestr("../escape",b"x")
                z.writestr(A.RECEIPT,"{}")
            with self.assertRaises(ValueError):A.Evidence(p)

if __name__=="__main__": unittest.main()
