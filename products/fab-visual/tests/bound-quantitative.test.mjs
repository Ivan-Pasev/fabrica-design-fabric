import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {auditBoundQuantitative,intervalBalance} from '../src/visual/bound-quantitative.mjs';
import {auditQuantitativeContract} from '../src/visual/quantitative-audit.mjs';
import {sha256,canonicalJSON} from '../src/visual/provenance.mjs';
const scene=JSON.parse(readFileSync(new URL('../templates/energy-microgrid.scene.json',import.meta.url),'utf8'));
const fixture=JSON.parse(readFileSync(new URL('../fixtures/bound-microgrid.synthetic.json',import.meta.url),'utf8'));
const copy=o=>structuredClone(o),audit=(sc=scene,b=fixture)=>auditBoundQuantitative(sc,copy(b));
const root=fileURLToPath(new URL('../',import.meta.url));

test('Ω11P trusted scene real canonical SHA-256 agrees with pinned synthetic fixture',()=>{
 const hash='sha256:'+sha256(canonicalJSON(scene));
 assert.equal(hash,'sha256:9ae22ab08570d4ea8164c1246c712381c5ba5d063eb057e8b99e15b6c6a0c53e');
 assert.equal(hash,fixture.sourceSceneDigest);
 assert.equal(fixture.sourceModel.revision,scene.model.revision);
});
test('nominal PASS but declared uncertainty interval INCONCLUSIVE and release HOLD',()=>{
 const report=audit();
 assert.equal(report.nominal.status,'PASS');
 assert.equal(report.status,'INCONCLUSIVE');
 assert.deepEqual(report.intervals.map(x=>x.classification),
   ['INCONCLUSIVE_OVERLAP','INCONCLUSIVE_OVERLAP']);
 assert.deepEqual(report.readouts.map(x=>x.status),['PASS','PASS','PASS']);
 assert.equal(report.physicalValidation,'NOT_RUN');
 assert.equal(report.hostAuthorization,'NOT_RUN');
 assert.equal(report.formalProof,'NOT_RUN');
 assert.equal(report.release,'HOLD');
});
test('intervals include zero nominal residual for both synthetic balances',()=>{
 const report=audit();
 for(const b of report.intervals){assert.ok(b.loSI<=0);assert.ok(b.hiSI>=0);assert.ok(b.loSI<b.hiSI);}
});
test('zero declared uncertainty has a safely enclosed PASS at nonzero stated tolerance',()=>{
 const e=copy(fixture);
 for(const b of e.quantitative.balances)for(const t of b.terms)t.uncertainty=0;
 const report=audit(scene,e);
 assert.equal(report.status,'PASS');
 assert.deepEqual(report.intervals.map(x=>x.classification),
   ['WITHIN_DECLARED_BOUNDS','WITHIN_DECLARED_BOUNDS']);
});
test('declared fixed imbalance with tiny uncertainty is a distinct interval FAIL',()=>{
 const e=copy(fixture);
 for(const b of e.quantitative.balances)for(const t of b.terms)t.uncertainty=0;
 e.quantitative.balances[0].terms[0].value=11;
 const r=audit(scene,e);
 assert.equal(r.nominal.status,'FAIL');
 assert.equal(r.status,'FAIL');
 assert.equal(r.intervals[0].classification,'OUTSIDE_DECLARED_BOUNDS');
});
test('source scene ID drift cannot be tolerated even if numbers remain unchanged',()=>{
 const s=copy(scene);s.id='forged-device-topology';
 assert.throws(()=>audit(s),/source scene digest drift/);
});
test('model authority change is blocked by source digest binding',()=>{
 const s=copy(scene);s.model.authority='REAL_SIGNED_ELECTRICITY_AUTHORITY';
 assert.throws(()=>audit(s),/source scene digest drift/);
});
test('source claim/observable payload changes fail closed',()=>{
 for(const mut of [
  s=>s.claim.status='CERTIFIED',
  s=>s.observables[0].value=777,
  s=>s.parts[0].x+=10,
  s=>s.links.pop()
 ]){
  const s=copy(scene);mut(s);
  assert.throws(()=>audit(s),/source scene digest drift/);
 }
});
test('forged sidecar digest or inconsistent model revision cannot proceed',()=>{
 const a=copy(fixture);a.sourceSceneDigest='sha256:'+'e'.repeat(64);
 assert.throws(()=>audit(scene,a),/source scene digest drift/);
 const b=copy(fixture);b.sourceModel.revision='0.6.0-production';
 assert.throws(()=>audit(scene,b),/model identity\/revision/);
});
test('wrong source representation and scene ID rejected',()=>{
 const a=copy(fixture);a.sourceRepresentation='PHYSICAL';
 assert.throws(()=>audit(scene,a),/model identity\/revision/);
 const b=copy(fixture);b.sourceSceneId='another';
 assert.throws(()=>audit(scene,b),/model identity\/revision/);
});
test('missing source pin and spoofed schema fail closed',()=>{
 for(const value of ['',null,'sha256:123']){
  const a=copy(fixture);a.sourceSceneDigest=value;
  assert.throws(()=>audit(scene,a),/original canonical SHA-256 required/);
 }
 const b=copy(fixture);b.schema='fab.visual.bound-quantitative.v2';
 assert.throws(()=>audit(scene,b),/exact source-bound envelope/);
});
test('forged model approvals cannot be smuggled as top-level sidecar keys',()=>{
 const a=copy(fixture);a.release='PASS';
 assert.throws(()=>audit(scene,a),/exact source-bound envelope/);
 const b=copy(fixture);b.publisherSignature='AUTHORIZED';
 assert.throws(()=>audit(scene,b),/exact source-bound envelope/);
});
test('structural count independently evaluated against actual scene shape',()=>{
 const r=audit();
 assert.deepEqual(r.readouts.slice(0,2).map(x=>x.actualSI),[6,7]);
 assert.equal(r.readouts[0].scope,'INDEPENDENT_SCENE_STRUCTURE_COUNT');
});
test('wrong independently evaluated count fails but does not change source model',()=>{
 const x=copy(fixture);x.readouts[0].expected=777;
 const r=audit(scene,x);
 assert.equal(r.readouts[0].status,'FAIL');
 assert.equal(r.status,'FAIL');
 assert.equal(scene.parts.length,6);
});
test('unit type mismatch on counts or declared values rejected',()=>{
 const a=copy(fixture);a.readouts[0].unit='kW';
 assert.throws(()=>audit(scene,a),/evaluator unit dimension mismatch/);
 const b=copy(fixture);b.readouts[2].unit='kW';
 assert.throws(()=>audit(scene,b),/evaluator unit dimension mismatch/);
});
test('numeric source observable is explicitly not an independently executed model',()=>{
 const r=audit();
 const x=r.readouts[2];
 assert.equal(x.actualSI,6);
 assert.equal(x.scope,'DECLARED_SOURCE_VALUE_COMPARISON_NOT_INDEPENDENT_MODEL_EVALUATION');
 assert.equal(r.modelEvaluation,'COUNTS_INDEPENDENT_SOURCE_OBSERVABLES_DECLARED_ONLY');
});
test('non-numeric synthetic source status cannot be represented as independently numeric',()=>{
 const a=copy(fixture);a.readouts[2].observableId='battery_soc';
 assert.throws(()=>audit(scene,a),/finite exact source observable required/);
});
test('no unknown evaluator, duplicate identity or arbitrary source paths',()=>{
 const a=copy(fixture);a.readouts[0].evaluator='RUN_JAVASCRIPT';
 assert.throws(()=>audit(scene,a),/invalid explicit bounded evaluator/);
 const b=copy(fixture);b.readouts[0].id='link_count';
 assert.throws(()=>audit(scene,b),/unique readout IDs/);
 const c=copy(fixture);c.readouts[0].execute='rm -rf';
 assert.throws(()=>audit(scene,c),/invalid explicit bounded evaluator/);
});
test('unreviewed measurement label against synthetic original scene refused',()=>{
 const x=copy(fixture);x.quantitative.source.kind='UNVERIFIED_MEASUREMENT';
 assert.throws(()=>audit(scene,x),/synthetic original scene cannot claim real measurement provenance/);
});
test('interval report retains no statistically independent sensor assumption',()=>{
 const x=audit().intervals[0];
 assert.equal(x.correlatedErrorIndependence,'NOT_ASSUMED');
 assert.equal(x.decimalInputEnclosure,'NOT_CERTIFIED');
 assert.equal(x.scientificValidation,'NOT_RUN');
});
test('nonfinite or invalid sidecar uncertainty rejects in inherited audit',()=>{
 const e=copy(fixture);e.quantitative.balances[0].terms[0].uncertainty=-1;
 assert.throws(()=>audit(scene,e),/nonnegative finite absolute uncertainty/);
});
test('interval evaluator refuses lack of nominal validated receipt',()=>{
 assert.throws(()=>intervalBalance(fixture.quantitative.balances[0],null),/validated balance and nominal receipt required/);
});
test('malformed or incomplete trusted scene never yields bound evidence',()=>{
 assert.throws(()=>audit({id:'bad'}),/schema|parts|representation/);
});
test('CLI emits machine-readable INCONCLUSIVE and nonzero process status',()=>{
 const r=spawnSync(process.execPath,
 ['bin/fab-visual.mjs','audit-bound','templates/energy-microgrid.scene.json','fixtures/bound-microgrid.synthetic.json'],
 {cwd:root,encoding:'utf8'});
 assert.equal(r.status,2,r.stderr);
 const x=JSON.parse(r.stdout);
 assert.equal(x.status,'INCONCLUSIVE');
 assert.equal(x.release,'HOLD');
 assert.equal(x.sourceSceneDigest,fixture.sourceSceneDigest);
});
test('CLI accepts zero-uncertainty synthetic bound but cannot authorize release',()=>{
 const env=copy(fixture);
 for(const b of env.quantitative.balances)for(const t of b.terms)t.uncertainty=0;
 const r=audit(scene,env);
 assert.equal(r.status,'PASS');
 assert.equal(r.physicalValidation,'NOT_RUN');
 assert.equal(r.externalSourceAuthentication,'NOT_PRESENT');
});
