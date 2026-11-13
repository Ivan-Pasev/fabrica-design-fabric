import test from 'node:test';
import assert from 'node:assert/strict';
import {policyScene} from '../src/visual/fixture.mjs';
import {containmentIndex,verifyRefinement,requireRefinement} from '../src/visual/semantic-refinement.mjs';
const clone=x=>structuredClone(x);
function sample(){
  const p=policyScene();p.id='synthetic-storage';p.model={id:'fab.energy.synthetic',revision:'r1',authority:'fixture only'};
  p.parts=[{id:'rack',label:'Rack',x:10,y:10,w:110,h:80}];p.links=[];
  p.observables=[{id:'total_energy',value:24,unit:'kWh',source:'synthetic formula'}];
  const c=clone(p);c.id='synthetic-module-descent';c.parts=[{id:'moduleA',label:'Module A',x:10,y:10,w:45,h:60},{id:'moduleB',label:'Module B',x:65,y:10,w:45,h:60}];
  c.observables=[{id:'energy_A',value:10,unit:'kWh',source:'synthetic formula'},{id:'energy_B',value:14,unit:'kWh',source:'synthetic formula'}];
  const contract={schema:'fab.refinement.v0.1',parentSceneId:p.id,childSceneId:c.id,childToParent:{moduleA:'rack',moduleB:'rack'},aggregates:[{parentId:'total_energy',childIds:['energy_A','energy_B'],op:'sum',unit:'kWh',absTolerance:0.001}]};
  return {p,c,contract};
}
test('valid synthetic sum refinement is accepted with traceable residual',()=>{const {p,c,contract}=sample();const r=requireRefinement(p,c,contract);assert.equal(r.checks[0].derived,24);assert.equal(r.checks[0].delta,0)});
test('out-of-tolerance aggregation rejected',()=>{const {p,c,contract}=sample();c.observables[0].value=11;assert.equal(verifyRefinement(p,c,contract).status,'FAIL')});
test('missing unit rejected',()=>{const {p,c,contract}=sample();c.observables[0].unit='J';assert.equal(verifyRefinement(p,c,contract).status,'FAIL')});
test('forged broad tolerance blocked if not finite',()=>{const {p,c,contract}=sample();contract.aggregates[0].absTolerance=Infinity;assert.equal(verifyRefinement(p,c,contract).status,'FAIL')});
test('malformed contract and missing observable rejected',()=>{const {p,c,contract}=sample();contract.aggregates[0].childIds.push('notFound');assert.equal(verifyRefinement(p,c,contract).status,'FAIL')});
test('model revision mismatch rejected',()=>{const {p,c,contract}=sample();c.model.revision='r2';assert.equal(verifyRefinement(p,c,contract).status,'FAIL')});
test('representation change rejected',()=>{const {p,c,contract}=sample();c.representation='PHYSICAL';assert.equal(verifyRefinement(p,c,contract).status,'FAIL')});
test('unknown part mapping rejected',()=>{const {p,c,contract}=sample();contract.childToParent.moduleB='fabricated';assert.equal(verifyRefinement(p,c,contract).status,'FAIL')});
test('part maps must be exhaustive and nonself',()=>{const {p,c,contract}=sample();delete contract.childToParent.moduleB;assert.equal(verifyRefinement(p,c,contract).status,'FAIL')});
test('duplicate source observable rejected',()=>{const {p,c,contract}=sample();contract.aggregates[0].childIds=['energy_A','energy_A'];assert.equal(verifyRefinement(p,c,contract).status,'FAIL')});
test('feedback loops are allowed but containment remains acyclic',()=>{const s=policyScene();s.links.push({from:'release',to:'intake',flow:'control'});s.parts[1].parent='intake';const r=containmentIndex(s);assert.equal(r.ranks.policy,1);assert.ok(r.children.intake.includes('policy'))});
test('containment cycles are rejected at SceneIR gate',()=>{const s=policyScene();s.parts[0].parent='policy';s.parts[1].parent='intake';assert.throws(()=>containmentIndex(s),/containment cycle/)});
test('no unqualified or nonnumeric aggregates',()=>{const {p,c,contract}=sample();c.observables[0].value='unknown';assert.equal(verifyRefinement(p,c,contract).status,'FAIL')});
test('identity operation requires one child',()=>{const {p,c,contract}=sample();contract.aggregates[0].op='identity';assert.equal(verifyRefinement(p,c,contract).status,'FAIL')});
test('mean operation checks parent value within tolerance',()=>{const {p,c,contract}=sample();p.observables[0].value=12;contract.aggregates[0].op='mean';assert.equal(verifyRefinement(p,c,contract).status,'PASS')});
