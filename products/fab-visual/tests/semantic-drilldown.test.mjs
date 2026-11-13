import test from 'node:test';
import assert from 'node:assert/strict';
import {policyScene} from '../src/visual/fixture.mjs';
import {renderSemanticDrilldown} from '../src/visual/semantic-drilldown.mjs';
function fixtures() {
 const p=policyScene();p.id='energy-main';p.model={id:'fabric.test.energy',revision:'v1',authority:'synthetic'};
 p.parts=[{id:'rack',label:'Rack',x:10,y:10,w:100,h:90}];p.links=[];
 p.observables=[{id:'e',value:8,unit:'kWh',source:'synthetic'}];
 const c=structuredClone(p);c.id='energy-component';c.parts=[{id:'c1',label:'C1',x:10,y:10,w:30,h:40},{id:'c2',label:'C2',x:70,y:10,w:30,h:40}];
 c.observables=[{id:'a',value:3,unit:'kWh',source:'synthetic'},{id:'b',value:5,unit:'kWh',source:'synthetic'}];
 const spec={schema:'fab.refinement.v0.1',parentSceneId:p.id,childSceneId:c.id,childToParent:{c1:'rack',c2:'rack'},aggregates:[{parentId:'e',childIds:['a','b'],op:'sum',unit:'kWh',absTolerance:0}]};
 return {p,c,spec};
}
test('semantic drilldown carries both exact identities and bounded evidence',()=>{const {p,c,spec}=fixtures();const h=renderSemanticDrilldown(p,c,spec);assert.match(h,/data-part=\\?"rack/);assert.match(h,/data-part=\\?"c1/);assert.match(h,/DECLARED_NUMERIC_REFINEMENT_NOT_EMPIRICAL_VALIDATION/);assert.match(h,/scientific validation/i);});
test('semantic drilldown blocks mismatched aggregate before HTML creation',()=>{const {p,c,spec}=fixtures();c.observables[0].value=33;assert.throws(()=>renderSemanticDrilldown(p,c,spec),/semantic refinement rejected/)});
test('malicious claim text is escaped in HTML and embedded data',()=>{const {p,c,spec}=fixtures();c.claim.interpretation='</script><img src=x onerror=alert(1)>';const h=renderSemanticDrilldown(p,c,spec);assert.doesNotMatch(h,/<img src=x/);assert.doesNotMatch(h,/<\/script><img/);});
