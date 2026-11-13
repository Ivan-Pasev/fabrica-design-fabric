import test from 'node:test';
import assert from 'node:assert/strict';
import {policyScene} from '../src/visual/fixture.mjs';
import {verifySyntheticPolicySnapshot,verifyPolicyTimeline} from '../src/adapters/policy-proof.mjs';
import {renderAnatomyTimeline} from '../src/adapters/anatomy-timeline.mjs';
const events=['START','POLICY_ESCALATE','HUMAN_APPROVE','RELEASE'];
const scenes=[policyScene([]),...events.map((_,i)=>policyScene(events.slice(0,i+1)))];
const clone=x=>structuredClone(x);
test('five generated frames have verified replayable event traces',()=>{
 assert.equal(verifyPolicyTimeline(scenes).status,'PASS');
 assert.equal(verifySyntheticPolicySnapshot(scenes.at(-1)).phase,'RELEASED');
});
test('model-authoritative timeline generated from pinned Anatomy geometry and five synchronized states',()=>{
 const html=renderAnatomyTimeline(scenes);
 assert.match(html,/Pinned Anatomy geometry/);
 assert.match(html,/max="4"/);
 assert.match(html,/id="frames"/); // script id, state data
 assert.ok(!html.includes('UNVERIFIED_HOST_APPROVAL'));
});
test('forged authorized observable rejected despite valid source geometry',()=>{
 const invalid=scenes.map(clone);invalid[2].observables.find(x=>x.id==='authorized').value=true;
 assert.equal(verifyPolicyTimeline(invalid).status,'FAIL');
 assert.throws(()=>renderAnatomyTimeline(invalid),/event-trace proof failed/);
});
test('forged RELEASED part at wrong model state rejected',()=>{
 const invalid=scenes.map(clone);invalid[1].parts.find(x=>x.id==='release').status='RELEASED';
 assert.equal(verifyPolicyTimeline(invalid).status,'FAIL');
});
test('invalid appended model events rejected even if visual claims otherwise',()=>{
 const invalid=scenes.map(clone);invalid[3].model.trace=['START','RELEASE'];
 assert.equal(verifyPolicyTimeline(invalid).status,'FAIL');
});
test('discontinuous timeline is rejected by append-only transition rule',()=>{
 const invalid=scenes.map(clone);invalid[2]=clone(scenes[0]);
 assert.equal(verifyPolicyTimeline(invalid).status,'FAIL');
});
