import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {evaluateIndependentMicrogrid} from '../src/visual/independent-model-evaluator.mjs';
import {sha256,canonicalJSON} from '../src/visual/provenance.mjs';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const original=read('../templates/energy-microgrid.scene.json');
const specimen=read('../fixtures/independent-microgrid.synthetic.json');
const copy=x=>structuredClone(x);
const audit=(s=original,q=specimen)=>evaluateIndependentMicrogrid(s,q);
test('M1 original source canonical hash matches fixed independent evaluator fixture',()=>{
 assert.equal('sha256:'+sha256(canonicalJSON(original)),specimen.sourceSceneDigest);
});
test('M1 calculates two independent synthetic equations without observing source readout',()=>{
 const r=audit();
 assert.equal(r.status,'PASS_BOUNDED_SYNTHETIC_EQUATION');
 assert.equal(r.power.actualSI,0);assert.equal(r.energy.actualSI,0);
 assert.equal(r.renderedReadout.status,'NOT_RUN');
 assert.equal(r.numericalPrecision,'BINARY64_FINITE_ARITHMETIC_NOT_EXACT_DECIMAL_PROOF');
 assert.equal(r.release,'HOLD');assert.equal(r.physicalValidation,'NOT_RUN');
 assert.equal(r.externalPublisherSignature,'NOT_PRESENT');
});
test('M1 conservation metamorphic uniform scale of all declared power inputs',()=>{
 const q=copy(specimen);
 for(const key of ['pv','batteryDischarge','load','conversionLoss'])
   q.inputs[key].value*=2;
 const r=audit(original,q);
 assert.equal(r.status,'PASS_BOUNDED_SYNTHETIC_EQUATION');
 assert.equal(r.power.actualSI,0);
});
test('M1 independent nonzero model computation identifies wrong claimed expected power',()=>{
 const q=copy(specimen);
 q.inputs.load.value=8;
 const r=audit(original,q);
 assert.equal(r.power.actualSI,1000);
 assert.equal(r.energy.actualSI,3600000);
 assert.equal(r.status,'FAIL');
});
test('M1 derived power and time metamorphism predicts independent watt-hours',()=>{
 const q=copy(specimen);
 q.inputs.load.value=8;
 q.expected.netPower={value:1,unit:'kW',tolerance:0};
 q.expected.netEnergy={value:1,unit:'kWh',tolerance:0};
 assert.equal(audit(original,q).status,'PASS_BOUNDED_SYNTHETIC_EQUATION');
 q.inputs.duration={value:2,unit:'h'};
 q.expected.netEnergy.value=2;
 assert.equal(audit(original,q).energy.actualSI,7200000);
 assert.equal(audit(original,q).status,'PASS_BOUNDED_SYNTHETIC_EQUATION');
});
test('M1 wrong model identifier and unauthorized equation cannot execute',()=>{
 const a=copy(specimen);a.equation='EVAL_SCENE_PROVIDED_CODE';
 assert.throws(()=>audit(original,a),/reviewed equation/);
 const b=copy(specimen);b.sourceModel.revision='production';
 assert.throws(()=>audit(original,b),/model identity/);
});
test('M1 source SHA, numeric observable, topology, claim tampering fail closed',()=>{
 for(const mut of [
 s=>s.parts.pop(),
 s=>s.claim.status='CERTIFIED',
 s=>s.observables[0].value=123,
 s=>s.model.authority='RELEASED'
 ]){
   const scene=copy(original);mut(scene);
   assert.throws(()=>audit(scene),/source SceneIR hash mismatch/);
 }
});
test('M1 deliberately changed source bound with numeric readout detects divergence',()=>{
 const scene=copy(original);
 scene.observables.find(o=>o.id==='site_export_power').value=7;
 scene.observables.find(o=>o.id==='site_export_power').evidence='NOT_RUN';
 const q=copy(specimen);
 q.sourceSceneDigest='sha256:'+sha256(canonicalJSON(scene));
 const r=audit(scene,q);
 assert.equal(r.renderedReadout.status,'FAIL');assert.equal(r.status,'FAIL');
});
test('M1 incompatible SI unit, offset and ambiguous dimensions fail closed',()=>{
 for(const unit of ['J','degC','kW/h','%']){
   const q=copy(specimen);q.inputs.pv.unit=unit;
   assert.throws(()=>audit(original,q),/finite nonnegative explicit SI-compatible quantity/);
 }
});
test('M1 forged status, publisher signature, new scripts are forbidden',()=>{
 for(const key of ['release','publisherSignature','execute']){
  const q=copy(specimen);q[key]='PASS';
  assert.throws(()=>audit(original,q),/exact reviewed equation and schema/);
 }
});
test('M1 negative, infinite and nonfinite declared power cannot be computed',()=>{
 for(const value of [-1,Infinity,NaN]){
  const q=copy(specimen);q.inputs.load.value=value;
  assert.throws(()=>audit(original,q),/finite nonnegative/);
 }
});
test('M1 zero or impossible duration cannot be accepted',()=>{
 for(const value of [0,-3,1e20]){
   const q=copy(specimen);q.inputs.duration.value=value;
   assert.throws(()=>audit(original,q),/finite nonnegative|outside bounded/);
 }
});
test('M1 expected power dimension and tolerance are explicit',()=>{
 const q=copy(specimen);q.expected.netPower.unit='kWh';
 assert.throws(()=>audit(original,q),/bounded expected/);
 const r=copy(specimen);r.expected.netPower.tolerance=-0.2;
 assert.throws(()=>audit(original,r),/bounded expected/);
});
test('M1 reject extra fields smuggling code or undeclared instrument status',()=>{
 const q=copy(specimen);q.inputs.privateMeasurement={value:999,unit:'W'};
 assert.throws(()=>audit(original,q),/exact microgrid inputs/);
 const r=copy(specimen);r.expected.netPower.claim='CERTIFIED';
 assert.throws(()=>audit(original,r),/bounded expected/);
});
test('M1 finite stressed cancellation remains bounded/explicitly binary64',()=>{
 const q=copy(specimen);
 q.inputs.pv={value:1000000,unit:'W'};
 q.inputs.batteryDischarge={value:1,unit:'W'};
 q.inputs.load={value:1000000,unit:'W'};
 q.inputs.conversionLoss={value:1,unit:'W'};
 assert.equal(audit(original,q).power.actualSI,0);
 assert.equal(audit(original,q).formalProof,'NOT_RUN');
});
