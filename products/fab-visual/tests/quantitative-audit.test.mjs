import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {getUnit,auditQuantitativeContract,auditAnatomyProjectionBasis} from '../src/visual/quantitative-audit.mjs';
import * as K from '../vendor/anatomy/kit/iso-kit.mjs';
import {verifyAnatomyBlobs} from '../src/adapters/anatomy-kernel.mjs';

const fixture=JSON.parse(readFileSync(new URL('../fixtures/quantitative-microgrid.synthetic.json',import.meta.url),'utf8'));
const clone=x=>structuredClone(x);
const audit=x=>auditQuantitativeContract(x??clone(fixture));

test('Ω11O synthetic energy/voltage SI dimension exponents and scaling are exact',()=>{
 assert.deepEqual(getUnit('kW').exponents,[1,2,-3,0,0,0,0]);
 assert.deepEqual(getUnit('kWh').exponents,[1,2,-2,0,0,0,0]);
 assert.deepEqual(getUnit('A').exponents,[0,0,0,1,0,0,0]);
 assert.deepEqual(getUnit('Pa').exponents,[1,-1,-2,0,0,0,0]);
 assert.equal(getUnit('Wh').toSI,3600);
 assert.equal(getUnit('kWh').toSI,3600000);
 assert.equal(getUnit('MW').toSI,1000000);
 assert.equal(getUnit('m/s^2').dimension,'ACCELERATION');
});
test('Ω11O unknown, offset and ambiguous units fail instead of inference',()=>{
 for(const u of ['degC','°C','F','kW/h','m3','ton','US_gallon','m.s^-1',null,''])assert.throws(()=>getUnit(u),/unknown unit/);
});
test('two model-defined conservation examples PASS arithmetic only; never PHYSICAL',()=>{
 const r=audit();
 assert.equal(r.status,'PASS');
 assert.equal(r.release,'HOLD');
 assert.equal(r.physicalValidation,'NOT_RUN');
 assert.equal(r.independentRendererValidation,'NOT_RUN');
 assert.equal(r.scientificCertification,'NOT_RUN');
 assert.equal(r.hostAuthorization,'NOT_RUN');
 assert.equal(r.balances.length,2);
 assert.equal(r.logic.status,'PASS');
 for(const x of r.balances){
   assert.equal(x.status,'PASS');
   assert.equal(x.absoluteResidualSI,0);
   assert.equal(x.interpretation,'DECLARED_INPUT_NUMERICAL_BALANCE_ONLY');
   assert.equal(x.uncertaintyRule,'TRIANGLE_INEQUALITY_NO_INDEPENDENCE_ASSUMED');
 }
 assert.equal(r.balances[0].uncertaintyWorstCaseSI,140);
});
test('kWh/Wh and W/kW conversion numerically agrees with SI balances',()=>{
 const r=audit();
 assert.equal(r.balances[0].termCount,4);
 assert.equal(r.balances[0].terms[1].SI,3000);
 assert.equal(r.balances[1].terms[0].SI,12960000);
 assert.equal(r.balances[1].terms[1].SI,12960000);
});
test('non-conservation produces FAIL even when text claims success',()=>{
 const x=clone(fixture);
 x.balances[0].terms[2].value=9.2;
 const r=audit(x);
 assert.equal(r.status,'FAIL');
 assert.equal(r.balances[0].status,'FAIL');
 assert.ok(r.balances[0].absoluteResidualSI>100);
 assert.equal(r.release,'HOLD');
});
test('absolute tolerance is checked only in compatible dimensions',()=>{
 const x=clone(fixture);
 x.balances[0].tolerance.unit='J';
 assert.throws(()=>audit(x),/tolerance must match/);
});
test('a Watt cannot be added to a Joule, regardless of coincident values',()=>{
 const x=clone(fixture);
 x.balances[0].terms[1].unit='J';
 assert.throws(()=>audit(x),/incommensurate unit/);
});
test('relative tolerance uses absolute SI input magnitudes not cancellation',()=>{
 const x=clone(fixture);
 x.balances[0].terms[2].value+=0.2;
 x.balances[0].tolerance.relative=0.02;
 assert.equal(audit(x).balances[0].status,'PASS');
 x.balances[0].tolerance.relative=0.00001;
 assert.equal(audit(x).balances[0].status,'FAIL');
});
test('tolerance and uncertainties may not be negative, NaN or infinite',()=>{
 for(const invalid of [-1,NaN,Infinity,-Infinity]){
   const x=clone(fixture);x.balances[0].tolerance.absolute=invalid;
   assert.throws(()=>audit(x),/nonnegative absolute and relative tolerances/);
   const y=clone(fixture);y.balances[0].terms[1].uncertainty=invalid;
   assert.throws(()=>audit(y),/nonnegative finite absolute uncertainty/);
 }
});
test('source reference required, rather than generative claim attribution',()=>{
 const x=clone(fixture);x.balances[0].terms[0].source='';
 assert.throws(()=>audit(x),/term source reference required/);
});
test('duplicate balance/term identifiers and invalid lengths fail closed',()=>{
 const a=clone(fixture);a.balances.push(clone(a.balances[0]));
 assert.throws(()=>audit(a),/unique bounded balance IDs/);
 const b=clone(fixture);b.balances[0].terms[1].id='pv';
 assert.throws(()=>audit(b),/unique bounded term IDs/);
 const c=clone(fixture);c.balances[0].terms=[c.balances[0].terms[0]];
 assert.throws(()=>audit(c),/2–40 signed terms/);
});
test('nonfinite SI products/accumulated results cannot PASS',()=>{
 const x=clone(fixture);
 x.balances[0].terms[0].value=1e308;
 assert.throws(()=>audit(x),/SI conversion overflow|SI accumulated value overflow/);
});
test('non-numeric, unknown or mixed direction terms rejected',()=>{
 for(const val of [null,'9',NaN]){const x=clone(fixture);x.balances[0].terms[0].value=val;assert.throws(()=>audit(x),/finite signed contributions/)}
 const x=clone(fixture);x.balances[0].terms[0].direction='BOTH';
 assert.throws(()=>audit(x),/IN\/OUT required/);
});
test('finite graph checks all declared states, not just reachable status text',()=>{
 const x=clone(fixture);x.logic.states.push({id:'bad_orphan',released:true,authorization:'HOLD',evidence:'PASS'});
 const r=audit(x);
 assert.equal(r.logic.status,'FAIL');
 assert.deepEqual(r.logic.unreachableStates,['bad_orphan']);
 assert.equal(r.status,'FAIL');
 assert.match(r.logic.problems.join(','),/released without declared authorization/);
});
test('finite graph refuses authorization bypass through an event label',()=>{
 const x=clone(fixture);
 x.logic.transitions[1].event='SUBMIT';
 const r=audit(x);
 assert.equal(r.logic.status,'FAIL');
 assert.match(r.logic.problems.join(','),/approval without declared human approval event/);
});
test('finite graph refuses unguarded release transition',()=>{
 const x=clone(fixture);
 x.logic.transitions[2].event='SUBMIT';
 const r=audit(x);
 assert.equal(r.logic.status,'FAIL');
 assert.match(r.logic.problems.join(','),/released without declared release request/);
});
test('finite graph permits cycles while graph states are bounded',()=>{
 const r=audit();
 assert.equal(r.logic.status,'PASS');
 assert.equal(r.logic.checkedStates,4);
 assert.equal(r.logic.checkedTransitions,4);
 assert.equal(r.logic.reachableStates,4);
 assert.equal(r.logic.realHumanApproval,'NOT_VERIFIED');
});
test('unknown finite graph state and transition event reject',()=>{
 for(const key of ['to','from']){
  const x=clone(fixture);x.logic.transitions[0][key]='ghost';
  assert.throws(()=>audit(x),/unknown graph transition endpoint/);
 }
 const x=clone(fixture);x.logic.transitions[0].event='AUTO_OVERRIDE';
 assert.throws(()=>audit(x),/unknown graph transition endpoint or event/);
});
test('state ID collisions and inconsistent status notation reject',()=>{
 const x=clone(fixture);x.logic.states[1].id='draft';
 assert.throws(()=>audit(x),/invalid or duplicated/);
 const y=clone(fixture);y.logic.states[1].authorization='MAYBE';
 assert.throws(()=>audit(y),/invalid or duplicated/);
});
test('projection vectors are orthonormal and right-handed at widely varied cameras',()=>{
 for(const azimuth of [-160,-45,0,30,90,147]){
   for(const elevation of [1,10,30,45,70,89]){
     const r=auditAnatomyProjectionBasis({origin:[220,150],scale:2,azimuth,elevation});
     assert.equal(r.status,'PASS');
     assert.ok(r.orthogonalityResidual<1e-12);
     assert.ok(Math.abs(r.orientation-1)<1e-12);
     assert.equal(r.release,'HOLD');
     assert.match(r.informationLoss,/NON_INJECTIVE/);
   }
 }
});
test('independent projection decomposition matches pinned Anatomy K.iso on sample coordinates',()=>{
 assert.equal(verifyAnatomyBlobs().ok,true);
 const P={origin:[110,143],scale:2,azimuth:47,elevation:32};
 const b=auditAnatomyProjectionBasis(P);
 const dot=(a,p)=>a.reduce((z,v,i)=>z+v*p[i],0);
 const k=b.projectionKernel[0];
 for(const xyz of [[0,0,0],[17,34,5],[-20,50,83],[0,-9,-12]]){
   const ours=[P.origin[0]+dot(b.right,xyz)*k,P.origin[1]+dot(b.down,xyz)*k];
   const upstream=K.iso(xyz,P);
   for(let i=0;i<2;i++)assert.ok(Math.abs(ours[i]-upstream[i])<1e-9);
 }
});
test('invalid projection and edge cases fail closed without claiming real depth',()=>{
 for(const changes of [{elevation:0},{elevation:90},{scale:0},{scale:-1},{azimuth:NaN},{origin:[0]},{origin:[0,Infinity]}]){
   const x={origin:[0,0],scale:1,azimuth:45,elevation:30,...changes};
   assert.throws(()=>auditAnatomyProjectionBasis(x),/finite projection camera/);
 }
});
test('CLI audit-quantitative returns machine-readable report with explicit HOLD and no write',()=>{
 const root=fileURLToPath(new URL('../',import.meta.url));
 const result=spawnSync(process.execPath,['bin/fab-visual.mjs','audit-quantitative','fixtures/quantitative-microgrid.synthetic.json'],{cwd:root,encoding:'utf8'});
 assert.equal(result.status,0,result.stderr);
 const receipt=JSON.parse(result.stdout);
 assert.equal(receipt.status,'PASS');
 assert.equal(receipt.release,'HOLD');
 assert.equal(receipt.physicalValidation,'NOT_RUN');
});
test('CLI audit-quantitative invalid contract returns nonzero and no granted release',()=>{
 const root=fileURLToPath(new URL('../',import.meta.url));
 const result=spawnSync(process.execPath,['bin/fab-visual.mjs','audit-quantitative','fixtures/policy-scene.json'],{cwd:root,encoding:'utf8'});
 assert.notEqual(result.status,0);
 assert.match(result.stderr,/QUANTITATIVE_CONTRACT_REJECT/);
 assert.doesNotMatch(result.stdout,/ELIGIBLE_FOR_AUTHORIZED_RELEASE/);
});
