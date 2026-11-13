import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectorParts, inspectorCss, inspectorMarkup, inspectorRuntime} from '../src/visual/semantic-inspector.mjs';
import {renderAnatomyTimeline} from '../src/adapters/anatomy-timeline.mjs';
import {renderSemanticDrilldown} from '../src/visual/semantic-drilldown.mjs';
import {policyScene} from '../src/visual/fixture.mjs';

function policyTimeline(){
 const events=['START','POLICY_ESCALATE','HUMAN_APPROVE','RELEASE'];
 return Array.from({length:5},(_,i)=>policyScene(events.slice(0,i)));
}
function energyFixtures(){
 const p=policyScene();p.id='energy-main';p.model={id:'energy.synthetic',revision:'r1',authority:'synthetic'};p.parts=[{id:'rack',label:'Battery rack',x:10,y:10,w:180,h:120}];p.links=[];p.observables=[{id:'energy',value:24,unit:'kWh',source:'synthetic'}];p.claim.interpretation='Synthetic arithmetic illustration';
 const c=structuredClone(p);c.id='energy-child';c.parts=[{id:'moduleA',label:'Module A',x:10,y:10,w:80,h:80},{id:'moduleB',label:'Module B',x:130,y:10,w:80,h:80}];c.observables=[{id:'a',value:10,unit:'kWh',source:'synthetic'},{id:'b',value:14,unit:'kWh',source:'synthetic'}];
 const spec={schema:'fab.refinement.v0.1',parentSceneId:p.id,childSceneId:c.id,childToParent:{moduleA:'rack',moduleB:'rack'},aggregates:[{parentId:'energy',childIds:['a','b'],op:'sum',unit:'kWh',absTolerance:0}]};return {p,c,spec};
}

test('inspector only projects existing model identities and state without mutating input',()=>{
 const scene=policyScene();const before=structuredClone(scene);
 const parts=inspectorParts(scene);
 assert.equal(parts.length,4);assert.deepEqual(parts.map(p=>p.id),scene.parts.map(p=>p.id));
 assert.equal(parts.find(x=>x.id==='release').status,'BLOCKED');
 assert.equal(parts.find(x=>x.id==='human').status,'NEUTRAL');
 assert.deepEqual(scene,before);
});
test('visual inspector offers accessible zoom + labeled status controls with 44px hit targets',()=>{
 assert.match(inspectorMarkup,/id="zoom-in"/);assert.match(inspectorMarkup,/id="part-list"/);
 assert.match(inspectorMarkup,/aria-live="polite"/);assert.match(inspectorCss,/min-height:44px/);
 assert.match(inspectorRuntime,/getBBox/);assert.match(inspectorRuntime,/textContent=part.label/);
 assert.doesNotMatch(inspectorRuntime,/innerHTML\s*=\s*part\./);
});
test('five-state timeline keeps inspectable identities/status bound to its snapshots',()=>{
 const scenes=policyTimeline();const html=renderAnatomyTimeline(scenes);
 assert.match(html,/Zoomable isometric diagram/);assert.match(html,/id="part-info"/);
 assert.match(html,/FabVisualInspector\(stage\)/);assert.match(html,/inspector.update\(f.parts\)/);
 assert.match(html,/"status":"RELEASED"/);
 assert.match(html,/"status":"BLOCKED"/);
});
test('synthetic refinement makes both parent and child component identities inspectable',()=>{
 const {p,c,spec}=energyFixtures();const html=renderSemanticDrilldown(p,c,spec);
 assert.match(html,/Zoomable semantic system view/);assert.match(html,/"id":"rack"/);
 assert.match(html,/"id":"moduleA"/);assert.match(html,/"id":"moduleB"/);
 assert.match(html,/inspector.update\(f.parts\)/);
 assert.match(html,/DECLARED_NUMERIC_REFINEMENT_NOT_EMPIRICAL_VALIDATION/);
});
test('part labels are JSON-escaped in HTML and never concatenated as live HTML',()=>{
 const {p,c,spec}=energyFixtures();
 const attack='</script><img src=x onerror=alert(1)>';
 c.parts[0].label=attack;
 const html=renderSemanticDrilldown(p,c,spec);
 assert.doesNotMatch(html,/<img src=x/);
 assert.doesNotMatch(html,/<\/script><img src=x/);
 assert.match(html,/\\u003cimg/);
});
test('timeline inspection cannot bypass synthetic model replay verification',()=>{
 const scenes=policyTimeline(); scenes[0].parts.find(p=>p.id==='release').status='RELEASED';
 assert.throws(()=>renderAnatomyTimeline(scenes),/policy|model|trace|status/i);
});
