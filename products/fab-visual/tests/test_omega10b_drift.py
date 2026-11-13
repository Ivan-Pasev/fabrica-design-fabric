"""Adversarial, synthetic non-network tests for the source-locked drift classifier."""
import base64
import importlib.util
import json
import shutil
import struct
import tempfile
import unittest
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent / 'scripts' / 'diagnose-upstream-drift.py'
if not SOURCE.is_file():
    SOURCE=Path(__file__).with_name('diagnose-upstream-drift.py') # local source sandbox
SPEC=importlib.util.spec_from_file_location('drift',SOURCE)
D=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(D)

class DriftControls(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='omega10b-test-')
        root=Path(self.tmp.name)
        self.baseline=root/'before';self.rebuilt=root/'after'
        self.baseline.mkdir();self.rebuilt.mkdir()
        self.original=D.FILES.copy()
        self.D={"V":[0,0,0.4539904997395468],"camera":{"k":1.4073101483323658,"cam":[0,1,0.4539904997395468]},"exit":[0,494.96303493827395],"labels":["safe"]}
        self.X=json.loads(json.dumps(self.D))
        self.X['V'][2]=0.45399049973954675
        self.X['camera']['k']=1.4073101483323662
        self.X['camera']['cam'][2]=0.45399049973954675
        self.X['exit'][1]=494.9630349382739
        p=[(159,174,4,65381,32767),(159,175,4,65318,32767),
           (218,236,8,65535,21488),(237,258,2,65446,32768),(240,269,10,61097,32767)]
        q=[(159,174,4,65381,32768),(159,175,4,65318,32768),
           (218,236,8,65535,44047),(237,258,2,65446,32767),(240,269,10,61097,32768)]
        def pack(t):return base64.b64encode(b''.join(struct.pack('>HHHHH',*r) for r in t)).decode('ascii')
        self.A={"parts":[1,2,3],"framed":{"hand":pack(p)}}
        self.B={"parts":[1,2,3],"framed":{"hand":pack(q)}}
        for path,(symbol,_) in D.FILES.items():
            if symbol=='D':x,y=self.D,self.X
            else:x,y=self.A,self.B
            for root,model in [(self.baseline,x),(self.rebuilt,y)]:
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text('HEAD\nconst '+symbol+' = '+json.dumps(model,separators=(',',':'))+';\nTAIL\n',encoding='utf-8')
        D.FILES={p:(sym,D.digest((self.baseline/p).read_bytes())) for p,(sym,_) in self.original.items()}

    def tearDown(self):
        D.FILES=self.original
        self.tmp.cleanup()

    def assertBad(self):
        report,code=D.run(self.baseline,self.rebuilt)
        self.assertEqual(code,2,report)
        self.assertEqual(report['diagnostic'],'FAIL_UNCLASSIFIED')
        self.assertEqual(report['release'],'HOLD')

    def test_bounded_drift_is_not_byte_parity(self):
        report,code=D.run(self.baseline,self.rebuilt)
        self.assertEqual(code,0,report)
        self.assertEqual(report['parity'],'FAIL')
        self.assertEqual(report['diagnostic'],'PASS_BOUNDED_NUMERIC_DIAGNOSIS')
        self.assertEqual(report['files'][2]['count_changed_records'],5)
        self.assertEqual(report['release'],'HOLD')

    def test_only_exact_identical_sources_have_pass_parity(self):
        for p in D.FILES:shutil.copyfile(self.baseline/p,self.rebuilt/p)
        report,code=D.run(self.baseline,self.rebuilt)
        self.assertEqual(code,0)
        self.assertEqual(report['parity'],'PASS')

    def test_code_injection_outside_payload_blocked(self):
        p=next(iter(D.FILES))
        f=self.rebuilt/p
        f.write_text(f.read_text().replace('TAIL','TAIL<script>alert(1)</script>'))
        self.assertBad()

    def test_changed_nonnumeric_field_blocked(self):
        p=next(iter(D.FILES));f=self.rebuilt/p
        f.write_text(f.read_text().replace('"safe"','"unsafe"'))
        self.assertBad()

    def test_numeric_field_outside_allowlist_blocked(self):
        p=next(iter(D.FILES));f=self.rebuilt/p
        f.write_text(f.read_text().replace('"labels":["safe"]', '"labels":["safe"],"new_numeric_field":9'))
        self.assertBad()

    def test_changed_part_indices_in_packed_binary_blocked(self):
        p=[p for p,(sym,_) in D.FILES.items() if sym=='DATA'][0]
        f=self.rebuilt/p;txt=f.read_text();data=json.loads(txt.split('const DATA = ')[1].split(';\nTAIL')[0])
        r=bytearray(base64.b64decode(data['framed']['hand']))
        r[0]=r[0]+1
        data['framed']['hand']=base64.b64encode(r).decode()
        f.write_text('HEAD\nconst DATA = '+json.dumps(data,separators=(',',':'))+';\nTAIL\n')
        self.assertBad()

    def test_out_of_bound_camera_delta_blocked(self):
        p=next(iter(D.FILES));f=self.rebuilt/p
        f.write_text(f.read_text().replace('1.4073101483323662','1.40731'))
        self.assertBad()

    def test_wrong_source_baseline_hash_blocked(self):
        p=next(iter(D.FILES));f=self.baseline/p
        f.write_text(f.read_text().replace('HEAD','ALTERED HEAD'))
        self.assertBad()

    def test_missing_packed_record_blocked(self):
        p=[p for p,(sym,_) in D.FILES.items() if sym=='DATA'][0]
        f=self.rebuilt/p;txt=f.read_text();data=json.loads(txt.split('const DATA = ')[1].split(';\nTAIL')[0]);raw=base64.b64decode(data['framed']['hand'])
        data['framed']['hand']=base64.b64encode(raw[:-10]).decode()
        f.write_text('HEAD\nconst DATA = '+json.dumps(data,separators=(',',':'))+';\nTAIL\n')
        self.assertBad()

    def test_noncanonical_packed_normal_delta_does_not_skip_identity_check(self):
        p=[p for p,(sym,_) in D.FILES.items() if sym=='DATA'][0]
        f=self.rebuilt/p;txt=f.read_text();data=json.loads(txt.split('const DATA = ')[1].split(';\nTAIL')[0]);r=bytearray(base64.b64decode(data['framed']['hand']))
        r[6:10]=struct.pack('>HH',10000,10000)
        data['framed']['hand']=base64.b64encode(r).decode()
        f.write_text('HEAD\nconst DATA = '+json.dumps(data,separators=(',',':'))+';\nTAIL\n')
        self.assertBad()

if __name__=='__main__':unittest.main()
