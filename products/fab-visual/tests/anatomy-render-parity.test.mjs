import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {anatomySceneModel,renderAnatomySvg,renderAnatomyHtml} from '../src/adapters/anatomy-kernel.mjs';
import {policyScene} from '../src/visual/fixture.mjs';
const fixture=JSON.parse(readFileSync(new URL('../fixtures/policy-scene.json',import.meta.url),'utf8'));
const clone=x=>structuredClone(x);
test('static Anatomy painter obeys upstream settled keys exactly',()=>{
 const model=anatomySceneModel(fixture);
 const svg=renderAnatomySvg(fixture);
 const ids=[...svg.matchAll(/<g class="part" data-part="([^"]+)" data-paint-index="(\d+)"/g)];
 assert.equal(ids.length,fixture.parts.length);
 assert.deepEqual(ids.map(x=>x[1]),model.paintOrder);
 assert.deepEqual(ids.map(x=>Number(x[2])),ids.map((_,i)=>i));
 assert.equal(model.audit.scope,'PINNED_SOLIDS_ONLY');
});
test('policy fixture is replayable and static output rejects a forged authorization',()=>{
 assert.equal(anatomySceneModel(fixture).audit.model_evidence.status,'PASS');
 const s=clone(fixture);s.observables.find(o=>o.id==='authorized').value=true;
 assert.throws(()=>renderAnatomySvg(s),/model replay\/observable parity failed/);
 assert.throws(()=>renderAnatomyHtml(s),/model replay\/observable parity failed/);
});
test('static renderer refuses RELEASED status before authorized model release',()=>{
 const s=clone(fixture);s.parts.find(p=>p.id==='release').status='RELEASED';
 assert.throws(()=>renderAnatomySvg(s),/model replay\/observable parity failed/);
});
test('static renderer refuses unproven policy claim with missing trace',()=>{
 const s=clone(fixture);delete s.model.trace;
 assert.throws(()=>renderAnatomySvg(s),/model replay\/observable parity failed/);
});
test('rendered connectors remain explicitly unverified, regardless of solids audit result',()=>{
 const m=anatomySceneModel(fixture);
 assert.equal(m.audit.status,'PASS');
 assert.equal(m.audit.connections.status,'NOT_RUN');
 assert.equal(m.audit.full_scene_assurance,'INCONCLUSIVE');
 assert.match(renderAnatomySvg(fixture),/LINKS NOT DEPTH-AUDITED/);
});
test('for unregistered models, scientific agreement is NOT_RUN not fabricated PASS',()=>{
 const s=clone(fixture);s.model.id='unregistered.example';s.model.authority='test only';
 const m=anatomySceneModel(s);
 assert.equal(m.audit.model_evidence.status,'NOT_RUN');
 assert.equal(m.audit.full_scene_assurance,'INCONCLUSIVE');
});
test('event-trace state in static fixture equals dynamically generated reference scene',()=>{
 const dynamic=policyScene(['START','POLICY_ESCALATE']);
 assert.deepEqual(fixture.model.trace,dynamic.model.trace);
 assert.deepEqual(fixture.observables,dynamic.observables);
});
