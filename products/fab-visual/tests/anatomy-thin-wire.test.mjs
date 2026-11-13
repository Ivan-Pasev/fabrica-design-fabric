import test from 'node:test';
import assert from 'node:assert/strict';
import {rayBoxIntersection,sampleTubeOcclusion} from '../src/adapters/independent-occlusion.mjs';
const projection={origin:[400,260],scale:1,azimuth:45,elevation:30};
const fixture={plateMin:[-5,-5,0],plateMax:[5,5,1],points:[[-4,0,-1],[4,0,-1]],projection,step:0.25};
test('independent ray-AABB intersection identifies visible plate in front of wire midpoint',()=>{
 const forward=[0.6123724356957946,0.6123724356957945,0.5];
 const hit=rayBoxIntersection([0,0,-1],forward,fixture.plateMin,fixture.plateMax);
 assert.ok(hit);assert.ok(hit.enter>0);assert.ok(hit.leave>hit.enter);
});
test('upstream sampled depth misses intentionally occluded 0.05-radius wire: fail closed INCONCLUSIVE',()=>{
 const out=sampleTubeOcclusion({...fixture,radius:0.05});
 assert.equal(out.analyticOccluded,true);
 assert.equal(out.upstreamPairs,0);
 assert.equal(out.assurance,'INCONCLUSIVE');
});
test('unresolved overlap is not silently promoted on thin 0.15-radius wire',()=>{
 const out=sampleTubeOcclusion({...fixture,radius:0.15});
 assert.equal(out.analyticOccluded,true);
 assert.equal(out.upstreamPairs,0);
 assert.equal(out.assurance,'INCONCLUSIVE');
});
test('wide wire detected by upstream; bounded sampled result does not claim universal proof',()=>{
 const out=sampleTubeOcclusion({...fixture,radius:0.55});
 assert.equal(out.analyticOccluded,true);
 assert.ok(out.upstreamPairs>0);
 assert.equal(out.assurance,'BOUNDED_SAMPLED');
});
test('changing scale relative to sample step changes the width threshold',()=>{
 const a=sampleTubeOcclusion({...fixture,radius:0.2});
 const b=sampleTubeOcclusion({...fixture,radius:0.2,step:0.05});
 assert.ok(a.threshold>b.threshold);assert.equal(a.assurance,'INCONCLUSIVE');
});
