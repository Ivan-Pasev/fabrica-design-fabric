import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {parseExactDecimal,rational,addExact,subExact,mulExact,
  cmpExact,jsonExact,exactModelInterval,auditExactInterval} from '../src/visual/exact-interval.mjs';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const scene=read('../templates/energy-microgrid.scene.json');
const spec=read('../fixtures/exact-microgrid.synthetic.json');
const clone=x=>structuredClone(x);
const audit=(s=scene,q=spec)=>auditExactInterval(s,q);
const pair=x=>jsonExact(x);
const f=(n,d)=>({numerator:String(n),denominator:String(d)});
test('M2 decimal 0.1 + 0.2 equals EXACT 3/10, never binary64 echo',()=>{
 assert.deepEqual(pair(addExact(parseExactDecimal('0.1'),parseExactDecimal('0.2'))),f(3,10));
 assert.deepEqual(pair(parseExactDecimal('1e-12')),pair(parseExactDecimal('0.000000000001')));
});
test('M2 decimal grammar supports optional sign/exponent and normalizes signed zero',()=>{
 assert.deepEqual(pair(parseExactDecimal('-0.000')),f(0,1));
 assert.deepEqual(pair(parseExactDecimal('+1.25e+2')),f(125,1));
 assert.deepEqual(pair(parseExactDecimal('-0.125')),f(-1,8));
 assert.deepEqual(pair(parseExactDecimal('5e-3')),f(1,200));
});
test('M2 rejects rounded JSON numeric input and ambiguous decimal notation',()=>{
 for(const bad of [0.1,NaN,Infinity,null,'','1_000','01','0.',' .1','.1',
   '1,2','1e99999999','1e+25','1e-25','1'.repeat(41),'1e309','0x10','1/2']){
  assert.throws(()=>parseExactDecimal(bad),/EXACT_INTERVAL_REJECT/);
 }
});
test('M2 arithmetic exact cancellation, positive denominator, sign and gcd',()=>{
 const q=rational(12n,-20n);assert.deepEqual(pair(q),f(-3,5));
 assert.deepEqual(pair(subExact(q,q)),f(0,1));
 assert.deepEqual(pair(mulExact(parseExactDecimal('3.6'),parseExactDecimal('3600'))),f(12960,1));
 assert.equal(cmpExact(parseExactDecimal('0.300'),parseExactDecimal('3e-1')),0);
});
test('M2 actual synthetic interval [-140,+140] W, energy [-504000,+504000] J',()=>{
 const r=audit();
 assert.equal(r.status,'INCONCLUSIVE');assert.equal(r.release,'HOLD');
 assert.deepEqual(r.power.intervalLoSI,f(-140,1));
 assert.deepEqual(r.power.intervalHiSI,f(140,1));
 assert.deepEqual(r.power.nominalSI,f(0,1));
 assert.deepEqual(r.energy.intervalLoSI,f(-504000,1));
 assert.deepEqual(r.energy.intervalHiSI,f(504000,1));
 assert.equal(r.power.classification,'INCONCLUSIVE_OVERLAP');
 assert.equal(r.energy.classification,'INCONCLUSIVE_OVERLAP');
 assert.equal(r.physicalValidation,'NOT_RUN');assert.equal(r.formalProof,'NOT_RUN');
 assert.equal(r.renderedReadout,'NOT_RUN');
});
test('M2 zero widths produce bounded PASS with positive exact tolerances',()=>{
 const q=clone(spec);
 for(const t of q.terms)t.uncertainty='0';
 assert.equal(audit(scene,q).status,'PASS_BOUNDED_EXACT_ARITHMETIC');
});
test('M2 strict outside interval is distinct from overlap',()=>{
 const q=clone(spec);
 for(const t of q.terms)t.uncertainty='0';
 q.terms[0].magnitude='8';
 assert.equal(audit(scene,q).status,'FAIL');
 assert.equal(audit(scene,q).power.classification,'OUTSIDE_DECLARED_BOUNDS');
});
test('M2 closed tolerance endpoints classify equality as WITHIN',()=>{
 const q=clone(spec);
 q.terms=[{id:'a',magnitude:'1',uncertainty:'0',unit:'W',direction:'IN'},
    {id:'b',magnitude:'0',uncertainty:'0',unit:'W',direction:'OUT'}];
 q.absoluteTolerance={value:'1',unit:'W'};
 q.expectedEnergy={value:'3600',unit:'J',tolerance:'0'};
 assert.equal(audit(scene,q).power.classification,'WITHIN_DECLARED_BOUNDS');
 assert.equal(audit(scene,q).status,'PASS_BOUNDED_EXACT_ARITHMETIC');
});
test('M2 fixed positive duration integrates exact power interval',()=>{
 const q=clone(spec);q.duration={value:'1',unit:'h'};
 assert.deepEqual(audit(scene,q).energy.intervalLoSI,f(-504000,1));
 q.duration={value:'3600000',unit:'ms'};
 assert.deepEqual(audit(scene,q).energy.intervalHiSI,f(504000,1));
});
test('M2 rejects source model/claims/topology drift and forged digest',()=>{
 const q=clone(spec);q.sourceSceneDigest='sha256:'+'a'.repeat(64);
 assert.throws(()=>audit(scene,q),/digest drift/);
 const b=clone(spec);b.sourceModel.revision='certified';
 assert.throws(()=>audit(scene,b),/identity\/revision/);
 const s=clone(scene);s.claim.status='CERTIFIED';
 assert.throws(()=>audit(s),/digest drift/);
 const t=clone(scene);t.parts[0].x++;
 assert.throws(()=>audit(t),/digest drift/);
});
test('M2 forbids forged external authority, dynamic evaluator and release promotion',()=>{
 for(const field of ['release','publisherSignature','execute','script','measured']){
  const q=clone(spec);q[field]='AUTHORIZED';
  assert.throws(()=>audit(scene,q),/unreviewed exact model schema/);
 }
 const q=clone(spec);q.equation='RUN_SCENE_JAVASCRIPT';
 assert.throws(()=>audit(scene,q),/unreviewed exact model schema/);
});
test('M2 rejects unknown, affine, or mismatched units',()=>{
 for(const u of ['J','degC','°C','kW/h','%','unknown']){
  const q=clone(spec);q.terms[0].unit=u;
  assert.throws(()=>audit(scene,q),/dimensionally incompatible/);
 }
 const d=clone(spec);d.duration.unit='kW';
 assert.throws(()=>audit(scene,d),/dimensionally incompatible/);
 const e=clone(spec);e.absoluteTolerance.unit='J';
 assert.throws(()=>audit(scene,e),/dimensionally incompatible/);
});
test('M2 rejects negative uncertainty, duplicate identifiers, invalid term lengths',()=>{
 const q=clone(spec);q.terms[0].uncertainty='-0.1';
 assert.throws(()=>audit(scene,q),/nonnegative/);
 const r=clone(spec);r.terms[1].id='pv';
 assert.throws(()=>audit(scene,r),/unique signed term/);
 const s=clone(spec);s.terms=[];
 assert.throws(()=>audit(scene,s),/2–16 terms/);
});
test('M2 rejects doubled signed terms, nonpositive duration and unknown keys',()=>{
 const q=clone(spec);q.terms[0].direction='+-';
 assert.throws(()=>audit(scene,q),/signed term/);
 for(const x of ['0','-1']){
  const r=clone(spec);r.duration.value=x;
  assert.throws(()=>audit(scene,r),/positive/);
 }
 const s=clone(spec);s.terms[0].confidence='99%';
 assert.throws(()=>audit(scene,s),/signed term/);
});
test('M2 rejects unsupported relative tolerance and overly large input objects',()=>{
 const q=clone(spec);q.absoluteTolerance.relative='0.03';
 assert.throws(()=>audit(scene,q),/absolute tolerance/);
 const s=clone(spec);s.unused='x'.repeat(5000);
 assert.throws(()=>audit(scene,s),/unreviewed exact model schema|4096 bytes/);
});
test('M2 cannot label binary64 conversion exact or infer physical calibration',()=>{
 const r=audit();
 assert.equal(r.exactness,'CANONICAL_DECIMAL_STRING_TO_REDUCED_BIGINT_RATIONAL');
 assert.equal(r.externalSignature,'NOT_PRESENT');
 assert.equal(r.correlation,'NO_STATISTICAL_INDEPENDENCE_ASSUMED');
 assert.equal(r.toleranceMethod,'EXPLICIT_ABSOLUTE_EXACT_CLOSED_INTERVAL_ONLY');
 assert.equal(r.empiricalCalibration,'NOT_RUN');
});
test('M2 term operation rejects large magnitude and denominator limits',()=>{
 assert.throws(()=>parseExactDecimal('1e25'),/exponent/);
 assert.throws(()=>rational(10n**121n),/size limit/);
});
