import test from 'node:test';
import assert from 'node:assert/strict';
import {segmentIntersectsAabb2d,projectedPartBounds,analyzeProjectedLinks} from '../src/adapters/link-projection.mjs';
import {policyScene} from '../src/visual/fixture.mjs';
import {anatomySceneModel} from '../src/adapters/anatomy-kernel.mjs';
const R={x0:2,y0:2,x1:4,y1:4};
test('independent 2D analytic rectangle oracle catches crossings and tangencies',()=>{
 assert.equal(segmentIntersectsAabb2d([0,3],[6,3],R),true);
 assert.equal(segmentIntersectsAabb2d([0,2],[6,2],R),true);
 assert.equal(segmentIntersectsAabb2d([0,5],[6,5],R),false);
 assert.equal(segmentIntersectsAabb2d([0,0],[1,1],R),false);
});
test('degenerate point link only intersects if point lies inside projected bound',()=>{
 assert.equal(segmentIntersectsAabb2d([3,3],[3,3],R),true);
 assert.equal(segmentIntersectsAabb2d([8,3],[8,3],R),false);
});
test('projection corners and numeric guard are finite',()=>{
 const scene=policyScene(['START','POLICY_ESCALATE']);
 const p=anatomySceneModel(scene).projection;
 const b=projectedPartBounds(scene.parts[0],p);
 assert.ok(b.x1>b.x0 && b.y1>b.y0);
 assert.throws(()=>segmentIntersectsAabb2d([Infinity,0],[2,3],R));
});
test('reference links have bounded projected 2D clearance status',()=>{
 const scene=policyScene(['START','POLICY_ESCALATE']);
 const p=anatomySceneModel(scene).projection;
 const r=analyzeProjectedLinks(scene,p);
 assert.equal(r.assessedLinks,3);
 assert.equal(r.true3dRouteAndWireToWire,'NOT_RUN');
 assert.match(r.scope,/PROJECTED_/);
 assert.ok(['PASS','INCONCLUSIVE'].includes(r.status));
});
test('interposed third-party body forces INCONCLUSIVE, never PASS',()=>{
 const scene=policyScene(['START','POLICY_ESCALATE']);
 // A third-party part sits in the gap between two linked centers, without
 // overlapping either endpoint body in world coordinates.
 scene.parts[2]={...scene.parts[2],x:245,y:145,w:35,h:35};
 const p=anatomySceneModel(scene).projection;
 const r=analyzeProjectedLinks(scene,p);
 assert.equal(r.status,'INCONCLUSIVE');
 assert.ok(r.possibleObstructions.some(c=>c.possibleObstruction==='human'));
});
test('links with no non-endpoint components pass only narrow projected clearance',()=>{
 const s=policyScene(['START','POLICY_ESCALATE']);
 s.parts=s.parts.slice(0,2);s.links=s.links.slice(0,1);
 const p=anatomySceneModel(s).projection;
 const r=analyzeProjectedLinks(s,p);
 assert.equal(r.status,'PASS');
 assert.equal(r.assessedThirdPartyPairs,0);
 assert.equal(r.endpointClearance,'NOT_RUN');
});